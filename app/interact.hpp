#pragma once

#include <chrono>
#include <fmt/format.h>
#include <ostream>

#include <nitro/env/get.hpp>

#include "eval.hpp"
#include "httplib.h"
#include "modem.hpp"
#include "util.hpp"

namespace zebra
{

struct Coordinate
{
    UnderlyingInteger x;
    UnderlyingInteger y;

public:
    Coordinate(UnderlyingInteger x, UnderlyingInteger y) : x(x), y(y)
    {
    }
    Coordinate(const PExpr& expr)
    {
        const auto& [ex, ey] = zebra::as_vector(expr);
        this->x = ex->value();
        this->y = ey->value();
    }

    PExpr as_vector() const
    {
        return make_ap(make_ap(operators::cons, make_integer(this->x)), make_integer(this->y));
    }

    Coordinate up() const
    {
        return { x, y - 1 };
    }

    Coordinate down() const
    {
        return { x, y + 1 };
    }

    Coordinate left() const
    {
        return { x - 1, y };
    }

    Coordinate right() const
    {
        return { x + 1, y };
    }
};

inline bool operator==(const Coordinate& a, const Coordinate& b)
{
    return a.x == b.x && a.y == b.y;
}

inline std::ostream& operator<<(std::ostream& os, const Coordinate& expr)
{
    os << "<" << expr.x << ", " << expr.y << ">";
    return os;
}

class Interact
{
public:
    Interact(const std::string& protocol)
    : protocol_(make_operator(protocol)), apiclient_("icfpc2020-api.testkontur.ru", 443)
    {
    }

private:
    void step_(const PExpr& vector)
    {
        auto begin = now();
        auto proto_expr = make_ap(make_ap(this->protocol_, this->state_), vector);
        auto proto_result = this->evaluator.eval(proto_expr);
        auto end = now();
        fmt::print("step took {:.2f} ms\n", as_milliseconds(end - begin));

        auto fsd = as_list(proto_result);
        assert(fsd.size() == 3);
        PExpr flag = fsd.at(0);
        PExpr new_state = fsd.at(1);
        PExpr data = fsd.at(2);

        // std::cout << "fsd: " << flag << "\n" << ", " << new_state << ", " << data << "\n";
        this->state_ = new_state;
        if (flag->value() == 0)
        {
            auto eimages = as_list(data);
            std::cout << "draw " << eimages.size() << " images: (";
            images.clear();
            for (const auto& eimage : eimages)
            {
                images.emplace_back();
                auto epixels = as_list(eimage);
                std::cout << epixels.size() << ", ";
                for (const auto& v : epixels)
                {
                    images.back().emplace_back(v);
                }
            }
            std::cout << ")\n";
        }
        else
        {
            this->step_(this->send_(data));
        }
    }

    PExpr send_(const PExpr& data)
    {
        auto path = "/aliens/send?apiKey=" + nitro::env::get("API_KEY");
        const std::shared_ptr<httplib::Response> serverResponse =
            apiclient_.Post(path.c_str(), zebra::modem::modulate(data), "text/plain");

        return zebra::modem::demodulate(serverResponse->body);
    }

public:
    void operator()(Coordinate coord)
    {
        step_(coord.as_vector());
    }

public:
    Evaluator evaluator;

    std::vector<std::vector<Coordinate>> images;

private:
    PExpr protocol_;
    PExpr state_ = operators::nil;
    httplib::SSLClient apiclient_;
};
} // namespace zebra
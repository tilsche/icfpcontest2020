#pragma once

#include <fmt/format.h>
#include <fmt/ostream.h>

#include <chrono>
#include <ostream>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <nitro/env/get.hpp>

#include "eval.hpp"
#include "httplib.h"
#include "modem.hpp"
#include "simple_expr.hpp"
#include "util.hpp"

namespace zebra
{

struct Coordinate
{
    UnderlyingInteger x;
    UnderlyingInteger y;

public:
    Coordinate() : x(0), y(0)
    {
    }
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

class ImageList : public std::vector<std::vector<Coordinate>>
{
public:
    ImageList()
    {
    }

    ImageList(PExpr expr)
    {
        auto eimages = as_list(expr);
        // std::cout << "draw " << eimages.size() << " images: (";
        for (const auto& eimage : eimages)
        {
            this->emplace_back();
            auto epixels = as_list(eimage);
            // std::cout << epixels.size() << ", ";
            for (const auto& v : epixels)
            {
                this->back().emplace_back(v);
            }
        }
    }
};

std::pair<Coordinate, Coordinate> bounding_box(const ImageList& image_list)
{
    Coordinate top_left{ 0, 0 };
    Coordinate bottom_right{ 0, 0 };
    for (const auto& image : image_list)
    {
        for (const auto& pixel : image)
        {
            top_left.x = std::min<UnderlyingInteger>(top_left.x, pixel.x);
            top_left.y = std::min<UnderlyingInteger>(top_left.y, pixel.y);
            bottom_right.x = std::max<UnderlyingInteger>(bottom_right.x, pixel.x);
            bottom_right.y = std::max<UnderlyingInteger>(bottom_right.y, pixel.y);
        }
    }
    return { top_left, bottom_right };
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
    std::tuple<int, PExpr, PExpr> ap_proto_(const PExpr& vector)
    {
        auto begin = now();
        auto proto_expr = make_ap(make_ap(this->protocol_, this->state_), vector);
        auto proto_result = this->evaluator.eval(proto_expr);
        auto end = now();
        // fmt::print("step took {:.2f} ms\n", as_milliseconds(end - begin));

        auto fsd = as_list(proto_result);
        assert(fsd.size() == 3);

        return { fsd.at(0)->value(), fsd.at(1), fsd.at(2) };
    }

    void step_(const PExpr& vector)
    {
        auto [flag, new_state, data] = ap_proto_(vector);

        this->state_ = new_state;
        if (flag == 0)
        {
            s_images = zebra::to_string(simple_data(data));
            images = ImageList(data);
            // std::cout << ")\n";
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
    void try_all()
    {
        auto [tl, br] = bounding_box(images);
        Coordinate c;

        auto s_state = zebra::to_string(simple_data(state_));

        candidates.clear();
        for (c.x = tl.x; c.x <= br.x; c.x++)
        {
            for (c.y = tl.y; c.y <= br.y; c.y++)
            {
                auto [flag, new_state, data] = ap_proto_(c.as_vector());
                auto s_new_state = zebra::to_string(simple_data(new_state));
                auto s_data = zebra::to_string(simple_data(data));

                fmt::print("{}", c);
                if (flag)
                {
                    //                    fmt::print(" send");
                }
                else
                {
                    if (s_data == this->s_images)
                    {
                        if (s_new_state == s_state)
                        {
                            //                            fmt::print(" unchanged\n");
                            continue;
                        }
                        //                        fmt::print(" same-images");
                    }
                }
                auto key = std::make_tuple(flag, s_new_state, s_data);
                if (candidates.contains(key))
                {
                    //                    fmt::print(" known candidate");
                }
                else
                {
                    //                    fmt::print(" Unique\n      {} | {} | {}\n", flag,
                    //                    s_new_state, s_data);
                }
                candidates[key].push_back(c);
                fmt::print("\n");
            }
        }
        fmt::print("all tries complete\n");
    }

public:
    void operator()(Coordinate coord)
    {
        candidates.clear();
        step_(coord.as_vector());
    }

public:
    Evaluator evaluator;
    std::unordered_map<std::tuple<int, std::string, std::string>, std::vector<Coordinate>>
        candidates;

    std::string s_images;
    ImageList images;

private:
    PExpr protocol_;
    PExpr state_ = operators::nil;
    httplib::SSLClient apiclient_;
};
} // namespace zebra

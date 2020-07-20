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
#include "flat_expr.hpp"
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
inline std::ostream& operator<<(std::ostream& os, const Coordinate& c)
{
    os << "<" << c.x << "," << c.y << ">";
    return os;
}

inline std::istream& operator>>(std::istream& in, Coordinate& c)
{
    char chr;
    in >> chr;
    if (!in)
    {
        return in;
    }
    assert(chr == '<');
    in >> c.x;
    in >> chr;
    assert(chr == ',');
    in >> c.y;
    in >> chr;
    assert(chr == '>');
    return in;
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

inline std::ostream& operator<<(std::ostream& os, const ImageList& il)
{
    os << "i[";
    for (const auto& image : il)
    {
        os << "[";
        for (const auto& pixel : image)
        {
            os << pixel << ",";
        }
        os << "],";
    }
    os << "]";
    return os;
}

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

class Interact
{
public:
    Interact(const std::string& protocol)
    : protocol_(make_operator(protocol)), apiclient_("icfpc2020-api.testkontur.ru", 443)
    {
        history_.emplace_back(operators::nil, ImageList());
    }

    void clear()
    {
        history_.clear();
        trace_.clear();
        candidates.clear();
        history_.emplace_back(operators::nil, ImageList());
    }

    template <class T>
    void save_trace(T& os)
    {
        for (auto c : trace_)
        {
            os << c << "\n";
        }
    }

    template <class T>
    void load_trace(T& is)
    {
        clear();
        Coordinate c;
        while (is >> c)
        {
            this->operator()(c);
        }
        notify();
    }

private:
    std::tuple<int, PExpr, PExpr> ap_proto_(const PExpr& state, const PExpr& vector)
    {
        auto begin = now();
        auto proto_expr = make_ap(make_ap(this->protocol_, state), vector);
        auto proto_result = this->evaluator.eval(proto_expr);
        auto end = now();
        // fmt::print("step took {:.2f} ms\n", as_milliseconds(end - begin));

        auto fsd = as_list(proto_result);
        assert(fsd.size() == 3);

        return { fsd.at(0)->value(), fsd.at(1), fsd.at(2) };
    }

    void step_(const PExpr& state, const PExpr& vector)
    {
        auto [flag, new_state, data] = ap_proto_(state, vector);

        if (flag == 0)
        {
            history_.emplace_back(new_state, ImageList(data));
        }
        else
        {
            this->step_(new_state, this->send_(data));
        }
    }

    PExpr send_(const PExpr& data)
    {
        std::cout << "Sending: " << flat_data(data) << std::endl;

        auto path = "/aliens/send?apiKey=" + nitro::env::get("API_KEY");
        const std::shared_ptr<httplib::Response> serverResponse =
            apiclient_.Post(path.c_str(), zebra::modem::modulate(data), "text/plain");

        auto expr = zebra::modem::demodulate(serverResponse->body);

        std::cout << "Received: " << flat_data(expr) << std::endl;
        return expr;
    }

public:
    void operator()(Coordinate coord)
    {
        trace_.emplace_back(coord);
        candidates.clear();
        step_(state(), coord.as_vector());
        notify();
    }

    void try_all()
    {
        auto [tl, br] = bounding_box(images());
        Coordinate c;

        auto s_state = zebra::to_string(simple_data(state()));
        auto s_images = zebra::to_string(images());

        candidates.clear();
        for (c.x = tl.x; c.x <= br.x; c.x++)
        {
            for (c.y = tl.y; c.y <= br.y; c.y++)
            {
                auto [flag, new_state, data] = ap_proto_(state(), c.as_vector());
                auto s_new_state = zebra::to_string(simple_data(new_state));
                auto s_data = zebra::to_string(simple_data(data));

                fmt::print("{}", c);
                if (flag)
                {
                    //                    fmt::print(" send");
                }
                else
                {
                    if (s_data == s_images)
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
        notify();
    }

    void undo()
    {
        candidates.clear();
        if (history_.size() < 2)
        {
            fmt::print("Cant undo any more!");
            return;
        }
        history_.pop_back();
        trace_.pop_back();
        notify();
    }

    void notify() const
    {
        for (const auto& l : listeners_)
        {
            l();
        }
    }

    void add_listener(const std::function<void()>& l)
    {
        listeners_.emplace_back(l);
    }

public:
    const PExpr& state() const
    {
        return history_.back().first;
    }

    const ImageList& images() const
    {
        return history_.back().second;
    }

public:
    Evaluator evaluator;
    std::unordered_map<std::tuple<int, std::string, std::string>, std::vector<Coordinate>>
        candidates;

    // one shorter as the history
    std::vector<Coordinate> trace_;

private:
    std::vector<std::pair<PExpr, ImageList>> history_;
    std::vector<std::function<void()>> listeners_;

    PExpr protocol_;
    httplib::SSLClient apiclient_;
};
} // namespace zebra

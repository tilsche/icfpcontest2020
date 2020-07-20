#pragma once

#include "interact.hpp"

#include <cassert>
#include <cmath>
#include <optional>
#include <vector>

namespace zebra
{

class BoundingBox
{
public:
    BoundingBox(Coordinate upper_left, Coordinate lower_right)
    : upper_left(upper_left), lower_right(lower_right)
    {
    }

    void add_point(Coordinate p)
    {
        upper_left.x = std::min(upper_left.x, p.x);
        upper_left.y = std::min(upper_left.y, p.y);

        lower_right.x = std::max(lower_right.x, p.x);
        lower_right.y = std::max(lower_right.y, p.y);
    }

    template <typename Functor>
    void visit(Functor f) const
    {
        for (int y = upper_left.y; y <= lower_right.y; y++)
        {
            for (int x = upper_left.x; x <= lower_right.x; x++)
            {
                f(Coordinate(x, y));
            }
        }
    }
    template <typename Functor>
    void visit_border(Functor f)
    {
        auto point = upper_left;

        while (point.x < lower_right.x)
        {
            f(point);
            point = point.right();
        }

        while (point.y < lower_right.y)
        {
            f(point);
            point = point.down();
        }

        while (point.x > upper_left.x)
        {
            f(point);
            point = point.left();
        }

        while (point.y > upper_left.y)
        {
            f(point);
            point = point.up();
        }
    }

    Coordinate size() const
    {
        return {
            lower_right.x - upper_left.x + 1,
            lower_right.y - upper_left.y + 1,
        };
    }

    Coordinate upper_left;
    Coordinate lower_right;
};

struct NumberResult
{
    zebra::Coordinate pivot;
    int size;
    UnderlyingInteger number;
};

class AlienNumberFinder
{
public:
    AlienNumberFinder(const std::vector<zebra::Coordinate>& points) : points_(points)
    {
    }

    std::optional<NumberResult> find_number_near(Coordinate point) const
    {
        static const UnderlyingInteger RADIUS = 4;

        BoundingBox bb{ { point.x - RADIUS, point.y - RADIUS },
                        { point.x + RADIUS, point.y + RADIUS } };

        for (UnderlyingInteger x = bb.upper_left.x; x <= bb.lower_right.x; x++)
        {
            for (UnderlyingInteger y = bb.upper_left.y; y <= bb.lower_right.y; y++)
            {
                auto res = parse_number({ x, y });
                if (res)
                    return res;
            }
        }

        return {};
    }

    std::optional<NumberResult> parse_number(Coordinate pivot) const
    {
        if (is_set(pivot))
        {
            return {};
        }
        else if (not_set(pivot.right()) || not_set(pivot.down()))
            return {};

        UnderlyingInteger size = -1;

        auto hrzt = pivot;
        auto vert = pivot;

        bool is_neg = false;

        while (true)
        {
            vert = vert.down();
            hrzt = hrzt.right();

            if (is_set(hrzt) && not_set(vert))
                return {};

            if (not_set(hrzt) && is_set(vert))
            {
                for (int i = 0; i <= size + 1; i++)
                {
                    vert = vert.right();
                    if (is_set(vert))
                        return {};
                }
                assert(vert.x == hrzt.x);
                is_neg = true;
                break;
            }

            if (not_set(hrzt) && not_set(vert))
                break;

            size++;

            if (size > 7)
                return {};
        }

        if (is_neg && size == 0)
            return {};

        assert(size >= 0);

        auto p = pivot.down().right();
        auto number_area = BoundingBox(p, { p.x + size, p.y + size });

        int i = 0;
        UnderlyingInteger number = 0;

        number_area.visit([this, &i, &number](Coordinate p) {
            if (this->is_set(p))
            {
                number += std::pow(2, i);
            }
            i++;
        });

        if (size > 1 && number == 0)
            return {};

        number_area.add_point(pivot);

        number_area.add_point(pivot.up().left());
        // We don't know why, but this doesn't work
        number_area.add_point(number_area.lower_right.down().right());

        auto has_empty_border = true;
        number_area.visit_border([this, &has_empty_border](Coordinate p) {
            if (this->is_set(p))
                has_empty_border = false;
        });

        if (!has_empty_border)
            return {};

        if (is_neg)
        {
            number = -number;
        }

        return { { pivot, size + 2, number } };
    }

    bool not_set(Coordinate point) const
    {
        return !is_set(point);
    }

    bool is_set(Coordinate point) const
    {
        for (auto p : points_)
        {
            if (point == p)
                return true;
        }
        return false;
    }

private:
    const std::vector<Coordinate>& points_;
};

} // namespace zebra
#pragma once

#include "interact.hpp"

#include <fmt/format.h>

namespace zebra
{
// 1: clicked points
// 0: available points
// 2: stage counter

class TTGrid
{
public:
    std::vector<std::vector<char>> data;

    TTGrid(const std::vector<Coordinate>& info)
    {
        data.resize(3, std::vector<char>(3, char(true)));
        for (auto c : info)
        {
            (*this)[c] = false;
        }
    }

    char operator[](Coordinate c) const
    {
        return data[c.x][c.y];
    }

    char& operator[](Coordinate c)
    {
        return data[c.x][c.y];
    }
};

bool solve_riddle(Interact& i, const std::vector<Coordinate>& stage)
{
    TTGrid clicked(i.images()[1]);
    TTGrid available(i.images()[0]);

    Coordinate c;
    for (c.x = 0; c.x < 3; c.x++)
    {
        for (c.y = 0; c.y < 3; c.y++)
        {
            if (available[c] and !clicked[c])
            {
                i(c);
                if (stage != i.images()[2])
                {
                    fmt::print("Riddle solved!\n");
                    return true;
                }
                // Only go deeper if not starting thingy
                if (i.images()[1].size() != 9)
                {
                    solve_riddle(i, stage);
                }
                i.undo();
            }
        }
    }
    return false;
}

void solve_riddle(Interact& i)
{
    auto current_state = i.images()[2];
    solve_riddle(i, current_state);
}
} // namespace zebra
#pragma once

#include <chrono>

namespace zebra
{

auto now()
{
    return std::chrono::system_clock::now();
}

template <class T>
double as_milliseconds(T duration)
{
    return std::chrono::duration_cast<std::chrono::duration<double, std::milli>>(duration).count();
}
} // namespace zebra
#pragma once

#include <string>
#include <string_view>

#include "expr.hpp"

namespace zebra::modem
{
std::string modulate_number(zebra::UnderlyingInteger num);
std::string modulate(PExpr expr);
std::int64_t demodulate_number(std::string_view input);
PExpr demodulate(std::string_view input);
} // namespace zebra::modem

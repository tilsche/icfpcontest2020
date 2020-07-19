#include <string>

#include "expr.hpp"

namespace zebra::modem
{
std::string modulate_number(zebra::UnderlyingInteger num);
std::string modulate(PExpr expr);
} // namespace zebra::modem

#include "modem.hpp"

#include <cmath>

#include <fmt/format.h>
#include <fmt/ostream.h>

#include <iostream>

namespace zebra::modem
{
std::string modulate_number(std::int64_t num)
{
    std::uint64_t abs_value = static_cast<std::uint64_t>(std::abs(num));
    if (abs_value == 0)
    {
        return std::string{ "010" };
    }
    else
    {
        auto len = 64 - __builtin_clzl(abs_value);
        auto n = (len + 3) & ~3;

        std::string unary_len{};
        for (int i = 0; i < (n / 4); ++i)
        {
            unary_len.push_back('1');
        }
        unary_len.push_back('0');

        std::cerr << fmt::format(
            "modulate_number: num={}, abs_value={}, unary_len={}, n={}, len={}\n", num, abs_value,
            unary_len, n, len);

        return fmt::format(
            "{pos_neg}{unary_len}{abs_value:0{n}b}", fmt::arg("pos_neg", num >= 0 ? "01" : "10"),
            fmt::arg("unary_len", unary_len), fmt::arg("n", n), fmt::arg("abs_value", abs_value));
    }
}

std::string modulate(PExpr expr)
{
    if (expr->is_integer())
    {
        std::cerr << "modulating number...\n";
        return modulate_number(expr->value());
    }
    else if (expr == operators::nil)
    {
        std::cerr << "modulating nil...\n";
        using namespace std::literals::string_literals;
        return "00"s;
    }
    else if (is_cons(expr))
    {
        std::cerr << "modulating cons...\n";
        const auto [head, tail] = as_vector(expr);

        auto head_str = modulate(head);
        auto tail_str = modulate(tail);

        return fmt::format("11{}{}", modulate(head), modulate(tail));
    }
    else
    {
        throw std::runtime_error(fmt::format("Expression '{}' is not modulateable", expr));
    }
}
} // namespace zebra::modem

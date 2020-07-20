#include "modem.hpp"

#include <charconv>
#include <cmath>
#include <iostream>
#include <utility>

#include <fmt/format.h>
#include <fmt/ostream.h>

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

        // std::cerr << fmt::format(
        //     "modulate_number: num={}, abs_value={}, unary_len={}, n={}, len={}\n", num,
        //     abs_value, unary_len, n, len);

        return fmt::format(
            "{pos_neg}{unary_len}{abs_value:0{n}b}", fmt::arg("pos_neg", num >= 0 ? "01" : "10"),
            fmt::arg("unary_len", unary_len), fmt::arg("n", n), fmt::arg("abs_value", abs_value));
    }
}

std::string modulate(PExpr expr)
{
    if (expr->is_integer())
    {
        // std::cerr << "modulating number...\n";
        return modulate_number(expr->value());
    }
    else if (expr == operators::nil)
    {
        // std::cerr << "modulating nil...\n";
        using namespace std::literals::string_literals;
        return "00"s;
    }
    else if (is_cons(expr))
    {
        // std::cerr << "modulating cons...\n";
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

std::pair<std::int64_t, std::string_view> demodulate_number_impl(std::string_view num)
{
    int bits = 0;

    // std::cerr << fmt::format("Parsing number: [{}]\n", num);

    auto remaining = num;
    while (true)
    {
        auto first = remaining.substr(0, 1);
        remaining = remaining.substr(1);

        if (first == "1")
        {
            bits += 1;
        }
        else
        {
            break;
        }
    }

    switch (bits)
    {
    case 0:
    {
        return { 0, remaining };
    }
    default:
    {
        auto len = 4 * bits;
        auto value = remaining.substr(0, len);
        auto rest = remaining.substr(len);

        // std::cerr << fmt::format("Found number: [{}|{}|{}], bits={}, remaining={}\n",
        //                          num.substr(0, bits + 1), value, rest, bits, remaining);

        std::int64_t parsed_value = 0;
        std::from_chars(value.begin(), value.end(), parsed_value, 2);
        return { parsed_value, rest };
    }
    }
}

std::int64_t demodulate_number(std::string_view num)
{
    auto [parsed, rest] = demodulate_number_impl(num);

    assert(rest.empty());

    return parsed;
}

std::pair<PExpr, std::string_view> demodulate_impl(std::string_view input)
{
    auto type = input.substr(0, 2);
    auto value = input.substr(2);

    // std::cerr << fmt::format("Demodulating: [{}|{}]\n", type, value);

    if (type == "00")
    {
        // std::cerr << "Demodulating nil...\n";
        return { operators::nil, value };
    }
    else if (type == "11")
    {
        // std::cerr << "Demodulating a list...\n";
        auto [head, rest] = demodulate_impl(value);
        auto [tail, left_over] = demodulate_impl(rest);

        return { make_ap(make_ap(operators::cons, head), tail), left_over };
    }
    else if (type == "01")
    {
        // std::cerr << "Demodulating a positive number...\n";
        auto [num_value, left_over] = demodulate_number_impl(value);

        return { make_integer(static_cast<UnderlyingInteger>(num_value)), left_over };
    }
    else if (type == "10")
    {
        // std::cerr << "Demodulating a negative number...\n";
        auto [num_value, left_over] = demodulate_number_impl(value);

        return { make_integer(-static_cast<UnderlyingInteger>(num_value)), left_over };
    }
    else
    {
        throw std::runtime_error(
            fmt::format("Unknown type '{}'; cannot demodulate '{}'", type, input));
    }
}
PExpr demodulate(std::string_view input)
{
    auto [expr, rest] = demodulate_impl(input);

    assert(rest.empty());

    return expr;
}
} // namespace zebra::modem

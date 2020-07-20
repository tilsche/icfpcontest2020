#pragma once

#include "expr.hpp"
#include "util.hpp"

#include <functional>
#include <memory>
#include <ostream>
#include <tuple>
#include <variant>

#include <nitro/lang/hash.hpp>
#include <nitro/lang/tuple_operators.hpp>

namespace zebra
{
struct SimpleCons;
struct SimpleNil
{
    std::size_t hash() const
    {
        return 402983;
    }
};
using PSimpleCons = std::shared_ptr<SimpleCons>;
using SimpleNode = std::variant<PSimpleCons, UnderlyingInteger, SimpleNil>;

struct SimpleCons : public nitro::lang::tuple_operators<SimpleCons>
{
    SimpleCons(const SimpleNode& head, const SimpleNode& tail) : head(head), tail(tail)
    {
    }

    SimpleNode head;
    SimpleNode tail;

    auto as_tuple()
    {
        return std::tie(head, tail);
    }
};

inline bool operator==(const SimpleNil& lhs, const SimpleNil& rhs)
{
    return true;
}

inline bool operator!=(const SimpleNil& lhs, const SimpleNil& rhs)
{
    return false;
}

SimpleNode simple_data(const PExpr& expr)
{
    if (expr->is_integer())
    {
        return { expr->value() };
    }
    if (expr == operators::nil)
    {
        return { SimpleNil() };
    }
    assert(is_cons(expr));
    return { std::make_shared<SimpleCons>(simple_data(expr->op()->arg()),
                                          simple_data(expr->arg())) };
}

inline std::ostream& operator<<(std::ostream& os, const SimpleNode& expr)
{
    if (std::holds_alternative<SimpleNil>(expr))
    {
        os << "nil";
    }
    else if (std::holds_alternative<UnderlyingInteger>(expr))
    {
        os << std::get<UnderlyingInteger>(expr);
    }
    else
    {
        const auto& cons = std::get<PSimpleCons>(expr);
        os << "(" << cons->head << "," << cons->tail << ")";
    }
    return os;
}
} // namespace zebra

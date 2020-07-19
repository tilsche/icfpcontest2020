#pragma once

#include <cstdint>

#include <memory>
#include <utility>
#include <variant>
#include <vector>

#include "util.hpp"

namespace zebra
{

using UnderlyingInteger = std::int64_t;

class Expr;

using PExpr = std::shared_ptr<Expr>;

class Expr
{
public:
    Expr(const PExpr& op, const PExpr& arg) : data_(OpArg_{ op, arg })
    {
    }

    Expr(const std::string& name) : data_(name)
    {
    }
    Expr(UnderlyingInteger i) : data_(i)
    {
    }

public:
    Expr(const Expr&) = delete;
    Expr(Expr&&) = delete;
    Expr& operator=(const Expr&) = delete;
    Expr& operator=(Expr&&) = delete;

public:
    bool is_ap() const
    {
        return std::holds_alternative<OpArg_>(this->data_);
    }

    bool is_integer() const
    {
        return std::holds_alternative<UnderlyingInteger>(this->data_);
    }

    bool is_function() const
    {
        return std::holds_alternative<std::string>(this->data_);
    }

    const PExpr& op() const
    {
        assert(this->is_ap());
        return std::get<OpArg_>(this->data_).op_;
    }

    const PExpr& arg() const
    {
        assert(this->is_ap());
        return std::get<OpArg_>(this->data_).arg_;
    }

    const std::string& name() const
    {
        assert(this->is_function());
        return std::get<std::string>(this->data_);
    }

    const PExpr& evaluated() const
    {
        return evaluated_;
    }

    UnderlyingInteger value() const
    {
        assert(this->is_integer());
        return std::get<UnderlyingInteger>(this->data_);
    }

    PExpr& evaluate(const PExpr& expr)
    {
        evaluated_ = expr;
        return evaluated_;
    }

private:
    struct OpArg_
    {
        PExpr op_;
        PExpr arg_;
    };

    PExpr evaluated_;

    using Data_ = std::variant<PExpr, OpArg_, UnderlyingInteger, std::string>;
    Data_ data_;
};

PExpr make_ap(const PExpr& op, const PExpr& arg)
{
#ifdef USE_AP_REGISTRY
    static std::unordered_map<std::pair<Expr*, Expr*>, PExpr, pair_hash> ap_registry;
    auto key = std::make_pair(op.get(), arg.get());
    auto it = ap_registry.find(key);
    if (it == ap_registry.end())
    {
        bool inserted;
        std::tie(it, inserted) = ap_registry.emplace(key, std::make_shared<Expr>(op, arg));
        assert(inserted);
    }
    return it->second;
#else
    return std::make_shared<Expr>(op, arg);
#endif
}

PExpr make_integer(UnderlyingInteger i)
{
#ifdef USE_INTEGER_REGISTRY
    static std::unordered_map<int, PExpr> number_registry;
    auto it = number_registry.find(i);
    if (it == number_registry.end())
    {
        bool inserted;
        std::tie(it, inserted) = number_registry.emplace(i, std::make_shared<Expr>(i));
        assert(inserted);
    }
    return it->second;
#else
    return std::make_shared<Expr>(i);
#endif
}

PExpr make_operator(const std::string& name)
{
    static std::unordered_map<std::string, PExpr> op_registry;
    auto it = op_registry.find(name);
    if (it == op_registry.end())
    {
        bool inserted;
        std::tie(it, inserted) = op_registry.emplace(name, std::make_shared<Expr>(name));
        assert(inserted);
    }
    return it->second;
}

namespace operators
{
    static PExpr cons = make_operator("cons");
    static PExpr t = make_operator("t");
    static PExpr f = make_operator("f");
    static PExpr nil = make_operator("nil");

    static PExpr neg = make_operator("neg");
    static PExpr i = make_operator("i");
    static PExpr isnil = make_operator("isnil");
    static PExpr car = make_operator("car");
    static PExpr cdr = make_operator("cdr");
    static PExpr add = make_operator("add");
    static PExpr mul = make_operator("mul");
    static PExpr div = make_operator("div");
    static PExpr lt = make_operator("lt");
    static PExpr eq = make_operator("eq");
    static PExpr s = make_operator("s");
    static PExpr c = make_operator("c");
    static PExpr b = make_operator("b");
} // namespace operators

std::vector<PExpr> as_list(const PExpr& expr)
{
    if (expr == operators::nil)
    {
        return {};
    }
    assert(expr->is_ap());
    assert(expr->op()->is_ap());
    assert(expr->op()->op() == operators::cons);

    auto tail = as_list(expr->arg());
    tail.insert(tail.begin(), expr->op()->arg());
    return tail;
}

std::pair<PExpr, PExpr> as_vector(const PExpr& expr)
{
    assert(expr->is_ap());
    assert(expr->op()->is_ap());
    assert(expr->op()->op() == operators::cons);

    return { expr->op()->arg(), expr->arg() };
}

// inline bool operator==(const Expr& lhs, const Expr& rhs)
//{
//    if (lhs.is_integer() && rhs.is_integer())
//    {
//        return lhs.value() == rhs.value();
//    }
//    return &lhs == &rhs;
//}
//
// inline bool operator!=(const Expr& lhs, const Expr& rhs)
//{
//    return lhs != rhs;
//}

inline std::ostream& operator<<(std::ostream& os, const PExpr& expr)
{
    if (expr->is_integer())
    {
        os << expr->value();
    }
    else if (expr->is_function())
    {
        os << expr->name();
    }
    else if (expr->is_ap())
    {
        os << "ap " << expr->op() << " " << expr->arg();
    }
    return os;
}

inline PExpr parse_expr(std::vector<std::string>::const_iterator& it,
                        std::vector<std::string>::const_iterator& end)
{
    assert(it != end);
    const auto token = *it;
    ++it;

    if (token == "ap")
    {
        PExpr op = parse_expr(it, end);
        PExpr arg = parse_expr(it, end);
        return make_ap(op, arg);
    }
    try
    {
        UnderlyingInteger i = std::stoll(token);
        return make_integer(i);
    }
    catch (const std::invalid_argument&)
    {
    }
    return make_operator(token);
}

inline PExpr parse_expr(const std::string& s)
{
    auto tokens = nitro::lang::split(s, " ");
    auto it = tokens.cbegin();
    auto end = tokens.cend();
    return parse_expr(it, end);
}
} // namespace zebra
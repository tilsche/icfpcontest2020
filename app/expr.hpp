#pragma once

#include <memory>

namespace zebra
{
enum class ExprType
{
    Integer,
    Function,
    Ap,
};

using UnderlyingInteger = long long;

class Expr;

using PExpr = std::shared_ptr<Expr>;

class Expr
{
public:
    Expr(const PExpr& op, const PExpr& arg) : type_(ExprType::Ap), op_(op), arg_(arg)
    {
    }

    Expr(const std::string& name) : type_(ExprType::Function), name_(name)
    {
    }
    Expr(UnderlyingInteger i) : type_(ExprType::Integer), integer_(i)
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
        return this->type_ == ExprType::Ap;
    }

    bool is_integer() const
    {
        return this->type_ == ExprType::Integer;
    }

    bool is_function() const
    {
        return this->type_ == ExprType::Function;
    }

    PExpr& op()
    {
        assert(this->is_ap());
        return this->op_;
    }

    const PExpr& op() const
    {
        assert(this->is_ap());
        return this->op_;
    }

    PExpr& arg()
    {
        assert(this->is_ap());
        return this->arg_;
    }

    const PExpr& arg() const
    {
        assert(this->is_ap());
        return this->arg_;
    }

    const std::string& name() const
    {
        assert(this->is_function());
        return this->name_;
    }

    const PExpr& evaluated() const
    {
        return evaluated_;
    }

    UnderlyingInteger value() const
    {
        assert(type_ == ExprType::Integer);
        return integer_;
    }

    ExprType type() const
    {
        return type_;
    }

    PExpr& evaluate(const PExpr& expr)
    {
        evaluated_ = expr;
        return evaluated_;
    }

private:
    ExprType type_;

    PExpr evaluated_;

    PExpr op_;
    PExpr arg_;
    UnderlyingInteger integer_;
    std::string name_;
};

PExpr make_ap(const PExpr& op, const PExpr& arg)
{
    return std::make_shared<Expr>(op, arg);
}

PExpr make_integer(UnderlyingInteger i)
{
    return std::make_shared<Expr>(i);
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
    switch (expr->type())
    {
    case ExprType::Integer:
        os << expr->value();
        break;
    case ExprType ::Function:
        os << expr->name();
        break;
    case ExprType ::Ap:
        os << "ap " << expr->op() << " " << expr->arg();
        break;
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
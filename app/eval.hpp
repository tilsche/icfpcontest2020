#pragma once

#include <cassert>

#include <memory>
#include <ostream>
#include <string>
#include <unordered_map>

#include <nitro/lang/string.hpp>

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
    UnderlyingInteger integer() const
    {
        assert(type_ == ExprType::Integer);
        return integer_;
    }

public:
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

inline bool operator==(const Expr& lhs, const Expr& rhs)
{
    if (lhs.type_ == ExprType::Integer && rhs.type_ == ExprType::Integer)
    {
        return lhs.integer_ == rhs.integer_;
    }
    return &lhs == &rhs;
}

inline bool operator!=(const Expr& lhs, const Expr& rhs)
{
    return lhs != rhs;
}

inline std::ostream& operator<<(std::ostream& os, const PExpr& expr)
{
    switch (expr->type_)
    {
    case ExprType::Integer:
        os << expr->integer_;
        break;
    case ExprType ::Function:
        os << expr->name_;
        break;
    case ExprType ::Ap:
        os << "ap " << expr->op_ << " " << expr->arg_;
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

class Evaluator
{
public:
    Evaluator()
    {
    }

    void add_function(const std::string& name, PExpr definition)
    {
        functions_[name] = definition;
    }

    void add_function(const std::string& line)
    {
        auto s = nitro::lang::split(line, " = ");
        assert(s.size() == 2);
        add_function(s.at(0), parse_expr(s.at(1)));
    }

    PExpr eval(PExpr expr)
    {
        if (expr->evaluated_)
        {
            return expr->evaluated_;
        }
        PExpr initial_expr = expr;
        while (true)
        {
            PExpr result = this->try_eval_(expr);
            if (result == expr)
            {
                initial_expr->evaluated_ = result;
                return result;
            }
            expr = result;
        }
    }

private:
    PExpr make_ap_(const PExpr& op, const PExpr& arg)
    {
        return zebra::make_ap(op, arg);
    }

    PExpr try_eval_(const PExpr& expr)
    {
        if (expr->evaluated_)
        {
            return expr->evaluated_;
        }
        if (expr->type_ == ExprType::Function)
        {
            // TODO find  some stuff
            if (auto it = this->functions_.find(expr->name_); it != this->functions_.end())
            {
                return it->second;
            }
            //            std::cout << "did not found " << expr->name_ << "\n";
        }
        if (expr->type_ == ExprType::Ap)
        {
            const auto& fun = eval(expr->op_);
            const auto& x = expr->arg_;
            if (fun->type_ == ExprType::Function)
            {
                if (fun == operators::neg)
                    return make_integer(-eval(x)->integer());
                if (fun == operators::i)
                    return x;
                if (fun == operators::nil)
                    return operators::t;
                if (fun == operators::isnil)
                    return this->make_ap_(
                        x,
                        this->make_ap_(operators::t, this->make_ap_(operators::t, operators::f)));
                if (fun == operators::car)
                    return this->make_ap_(x, operators::t);
                if (fun == operators::cdr)
                    return this->make_ap_(x, operators::f);
            }
            if (fun->type_ == ExprType::Ap)
            {
                PExpr fun2 = eval(fun->op_);
                PExpr y = fun->arg_;
                if (fun2->type_ == ExprType::Function)
                {
                    if (fun2 == operators::t)
                        return y;
                    if (fun2 == operators::f)
                        return x;
                    if (fun2 == operators::add)
                        return make_integer(eval(x)->integer() + eval(y)->integer());
                    if (fun2 == operators::mul)
                        return make_integer(eval(x)->integer() * eval(y)->integer());
                    if (fun2 == operators::div)
                        return make_integer(eval(y)->integer() / eval(x)->integer());
                    if (fun2 == operators::lt)
                        return eval(y)->integer() < eval(x)->integer() ? operators::t :
                                                                         operators::f;
                    if (fun2 == operators::eq)
                        return eval(x)->integer() == eval(y)->integer() ? operators::t :
                                                                          operators::f;
                    if (fun2 == operators::cons)
                        return this->eval_cons(y, x);
                }
                if (fun2->type_ == ExprType::Ap)
                {
                    PExpr fun3 = eval(fun2->op_);
                    PExpr z = fun2->arg_;
                    if (fun3->type_ == ExprType::Function)
                    {
                        if (fun3 == operators::s)
                            return this->make_ap_(this->make_ap_(z, x), this->make_ap_(y, x));
                        if (fun3 == operators::c)
                            return this->make_ap_(this->make_ap_(z, x), y);
                        if (fun3 == operators::b)
                            return this->make_ap_(z, this->make_ap_(y, x));
                        if (fun3 == operators::cons)
                            return this->make_ap_(this->make_ap_(x, z), y);
                    }
                }
            }
        }
        return expr;
    }

    PExpr eval_cons(const PExpr& a, const PExpr& b)
    {
        PExpr res = this->make_ap_(this->make_ap_(operators::cons, eval(a)), eval(b));
        res->evaluated_ = res;
        return res;
    }

public:
    std::unordered_map<std::string, PExpr> functions_;
};

} // namespace zebra

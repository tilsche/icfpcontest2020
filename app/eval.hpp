#pragma once

#include <cassert>

#include <fstream>
#include <memory>
#include <ostream>
#include <string>
#include <unordered_map>

#include <nitro/lang/string.hpp>

#include "expr.hpp"

namespace zebra
{

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

    void add_function_file(const std::string& filename)
    {
        std::ifstream f(filename);
        std::string line;
        while (std::getline(f, line))
        {
            this->add_function(line);
        }
    }

    PExpr eval(PExpr expr)
    {
        if (expr->evaluated())
        {
            return expr->evaluated();
        }
        PExpr initial_expr = expr;
        while (true)
        {
            //            std::cout << "eval " << expr << "\n";
            PExpr result = this->try_eval_(expr);
            if (result == expr)
            {
                initial_expr->evaluate(result);
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
        if (expr->evaluated())
        {
            return expr->evaluated();
        }
        if (expr->is_function())
        {
            // TODO find  some stuff
            if (auto it = this->functions_.find(expr->name()); it != this->functions_.end())
            {
                return it->second;
            }
            //            std::cout << "did not found " << expr->name_ << "\n";
        }
        if (expr->is_ap())
        {
            const auto& fun = eval(expr->op());
            const auto& x = expr->arg();
            if (fun->is_function())
            {
                if (fun == operators::neg)
                    return make_integer(-eval(x)->value());
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
            if (fun->is_ap())
            {
                PExpr fun2 = eval(fun->op());
                PExpr y = fun->arg();
                if (fun2->is_function())
                {
                    if (fun2 == operators::t)
                        return y;
                    if (fun2 == operators::f)
                        return x;
                    if (fun2 == operators::add)
                        return make_integer(eval(x)->value() + eval(y)->value());
                    if (fun2 == operators::mul)
                        return make_integer(eval(x)->value() * eval(y)->value());
                    if (fun2 == operators::div)
                        return make_integer(eval(y)->value() / eval(x)->value());
                    if (fun2 == operators::lt)
                        return eval(y)->value() < eval(x)->value() ? operators::t : operators::f;
                    if (fun2 == operators::eq)
                        return eval(x)->value() == eval(y)->value() ? operators::t : operators::f;
                    if (fun2 == operators::cons)
                        return this->eval_cons(y, x);
                }
                if (fun2->is_ap())
                {
                    PExpr fun3 = eval(fun2->op());
                    PExpr z = fun2->arg();
                    if (fun3->is_function())
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
        res->evaluate(res);
        return res;
    }

public:
    std::unordered_map<std::string, PExpr> functions_;
};

} // namespace zebra

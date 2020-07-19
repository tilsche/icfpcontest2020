#pragma once

#include "eval.hpp"

namespace zebra
{

struct Coordinate
{
    long long x;
    long long y;

public:
    PExpr as_vector() const
    {
        return make_ap(make_ap(operators::cons, make_integer(this->x)), make_integer(this->y));
    }
};

class Interact
{
public:
    Interact(const std::string& protocol) : protocol_(make_operator(protocol))
    {
    }

private:
    void step_(const PExpr& vector)
    {
        auto proto_expr = make_ap(make_ap(this->protocol_, this->state_), vector);
        auto proto_result = this->evaluator.eval(proto_expr);

        auto fsd = as_list(proto_result);
        assert(fsd.size() == 3);
        PExpr flag = fsd.at(0);
        PExpr new_state = fsd.at(1);
        PExpr data = fsd.at(2);

        std::cout << "fsd: " << flag << ", " << new_state << ", " << data << "\n";
        this->state_ = new_state;
        if (flag->value() == 0)
        {
            std::cout << "draw some stuff\n";
        }
        else
        {
            this->step_(this->send_(data));
        }
    }

    PExpr send_(const PExpr& data)
    {
        std::cout << "send some stuff\n";
        // TODO
        return data;
    }

public:
    void operator()(Coordinate coord)
    {
        step_(coord.as_vector());
    }

public:
    Evaluator evaluator;

private:
    PExpr protocol_;
    PExpr state_ = operators::nil;
};
} // namespace zebra
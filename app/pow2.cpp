#include <iostream>

#include "eval.hpp"

int main()
{
    auto pow2ex =
        zebra::parse_expr("ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1");
    std::cout << pow2ex << "\n";
    zebra::Evaluator e;
    e.add_function("pwr2", pow2ex);
    e.add_function("inc = ap add 1");

    std::cout << e.eval(zebra::parse_expr("ap inc 4")) << "\n";
    std::cout << e.eval(zebra::parse_expr("ap pwr2 4")) << "\n";
}
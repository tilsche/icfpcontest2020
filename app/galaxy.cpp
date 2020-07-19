#include <iostream>

#include "eval.hpp"
#include "interact.hpp"

int main()
{
    zebra::Interact i("galaxy");
    i.evaluator.add_function_file("../resources/galaxy.txt");

    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 0, 0 });
    i({ 8, 4 });
    i({ 2, -8 });
    i({ 3, 6 });
    i({ 0, -14 });
    i({ -4, 10 });
    i({ 9, -3 });
    i({ -4, 10 });
    i({ 1, 4 });
    i({ -78, 13 });
    i({ -7, 13 });
    i({ 1, 1 });
    //
    //    std::cout << e.eval(zebra::parse_expr("ap inc 4")) << "\n";
    //    std::cout << e.eval(zebra::parse_expr("ap pwr2 4")) << "\n";
}

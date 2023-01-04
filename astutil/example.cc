#include <iostream>
#include <stack>

#include "astutil.h"

using namespace astutil;

using expression = node<int, struct binary_expression>;

struct binary_expression {
    enum class op { add = 0, sub, mul, div } op_;
    expression lhs;
    expression rhs;

    auto children() { return std::tie(lhs, rhs); }
};

auto make_expression() {
    using bin = binary_expression;
    using op = binary_expression::op;

    return expression(bin{op::add, 1, bin{op::mul, 2, 3}});
}

struct printer {
    using op = binary_expression::op;

    auto enter(int const &e) const { std::cout << e << " "; }

    auto enter(binary_expression const &e) const {
        std::cout << "(";
        switch (e.op_) {
        case op::add:
            std::cout << "+";
            break;
        case op::sub:
            std::cout << "-";
            break;
        case op::mul:
            std::cout << "*";
            break;
        case op::div:
            std::cout << "/";
            break;
        }
        std::cout << " ";
    }

    auto exit(binary_expression const &) const { std::cout << ")"; }
};

struct evaluator {
    using op = binary_expression::op;

    std::stack<int> stack;

    auto exit(int const &e) { stack.push(e); }

    auto exit(binary_expression const &e) {
        if (stack.size() < 2) {
            throw std::runtime_error("stack underflow");
        }

        auto b = stack.top();
        stack.pop();
        auto a = stack.top();
        stack.pop();

        switch (e.op_) {
        case op::add:
            stack.push(a + b);
            break;
        case op::sub:
            stack.push(a - b);
            break;
        case op::mul:
            stack.push(a * b);
            break;
        case op::div:
            stack.push(a / b);
            break;
        }
    }
    auto result() const {
        if (stack.empty()) {
            throw std::runtime_error("stack underflow");
        }
        return stack.top();
    }
};

int main() {
    const auto expr = make_expression();

    printer p;
    expr.visit(p); // Prints "(+ 1 (* 2 3 ))"

    evaluator e;
    expr.visit(e);
    std::cout << " => " << e.result() << std::endl; // Prints " => 7"
}

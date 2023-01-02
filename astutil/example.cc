#include <iostream>
#include <stack>

#include "astutil.h"

using namespace astutil;

struct literal_expression;
struct binary_expression;

using expression = node<literal_expression, binary_expression>;

struct literal_expression {
    int value;
};

struct binary_expression {
    enum class op { add = 0, sub, mul, div };
    op op_;
    expression lhs;
    expression rhs;

    auto children() { return std::tie(lhs, rhs); }
};

auto make_expression() {
    using lit = literal_expression;
    using bin = binary_expression;
    using op = binary_expression::op;

    return expression(bin{op::add, lit{1}, bin{op::mul, lit{2}, lit{3}}});
}

struct printer {
    using op = binary_expression::op;

    auto enter(literal_expression const &e) const {
        std::cout << e.value << " ";
    }

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

    auto exit(literal_expression const &e) { stack.push(e.value); }

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
};

int main() {
    auto expr = make_expression();

    printer p;
    expr.visit(p); // Prints "(+ 1 (* 2 3 ))"

    evaluator e;
    expr.visit(e);
    std::cout << " => " << e.stack.top() << std::endl; // Prints " => 7"
}

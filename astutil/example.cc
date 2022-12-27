#include <iostream>
#include <stack>

#include "astutil.h"

using namespace astutil;

struct literal_expression;
struct binary_expression;

using expression = node<literal_expression, binary_expression>;

struct literal_expression : variant_of<expression> {
    int value;

    template<typename V>
    auto visit(V &&) {}
};

struct binary_expression : variant_of<expression> {
    enum class op { add = 0, sub, mul, div };
    op op_;
    expression lhs;
    expression rhs;

    template<typename V>
    auto visit(V &&vis) {
        lhs.visit(std::forward<V>(vis));
        rhs.visit(std::forward<V>(vis));
    }
};

auto make_expression() {
    using lit = literal_expression;
    using bin = binary_expression;
    using op = binary_expression::op;

    return make_node<bin>(
        op::add, make_node<lit>(1),
        make_node<bin>(op::mul, make_node<lit>(2), make_node<lit>(3)));
}

struct printer {
    using op = binary_expression::op;

    auto enter(literal_expression &e) { std::cout << e.value << " "; }

    auto enter(binary_expression &e) {
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

    auto exit(binary_expression &) { std::cout << ")"; }
};

struct evaluator {
    using op = binary_expression::op;

    std::stack<int> stack;

    auto exit(literal_expression &e) { stack.push(e.value); }

    auto exit(binary_expression &e) {
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

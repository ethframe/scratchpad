#include <iostream>
#include <stack>

#include "astutil.h"

using namespace astutil;

using expression = node<int, struct binary_expression, struct nary_expression>;

struct binary_expression {
    enum class op { add = 0, sub, mul, div } op_;
    expression lhs;
    expression rhs;

    auto children() { return std::tie(lhs, rhs); }
};

struct nary_expression {
    enum class op { sum = 0 } op_;
    expression::nodes args;

    auto children() { return std::tie(args); }
};

auto make_expression() {
    using bin = binary_expression;
    using nary = nary_expression;
    using bop = binary_expression::op;
    using nop = nary_expression::op;

    return expression{
        nary{nop::sum, {bin{bop::add, 1, bin{bop::mul, 2, 3}}, 8, 9}}};
}

struct printer {
    using bop = binary_expression::op;
    using nop = nary_expression::op;

    auto enter(int const &e) const { std::cout << e << " "; }

    auto enter(binary_expression const &e) const {
        std::cout << "(";
        switch (e.op_) {
        case bop::add:
            std::cout << "+";
            break;
        case bop::sub:
            std::cout << "-";
            break;
        case bop::mul:
            std::cout << "*";
            break;
        case bop::div:
            std::cout << "/";
            break;
        }
        std::cout << " ";
    }

    auto exit(binary_expression const &) const { std::cout << ") "; }

    auto enter(nary_expression const &e) const {
        std::cout << "(";
        switch (e.op_) {
        case nop::sum:
            std::cout << "sum";
            break;
        }
        std::cout << " ";
    }

    auto exit(nary_expression const &) const { std::cout << ") "; }
};

struct evaluator {
    using bop = binary_expression::op;
    using nop = nary_expression::op;

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
        case bop::add:
            stack.push(a + b);
            break;
        case bop::sub:
            stack.push(a - b);
            break;
        case bop::mul:
            stack.push(a * b);
            break;
        case bop::div:
            stack.push(a / b);
            break;
        }
    }

    auto exit(nary_expression const &e) {
        if (stack.size() < std::size(e.args)) {
            throw std::runtime_error("stack underflow");
        }

        switch (e.op_) {
        case nop::sum:
            auto sum = 0;
            for (std::size_t i = 0; i < std::size(e.args); ++i) {
                sum += stack.top();
                stack.pop();
            }
            stack.push(sum);
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
    expr.visit(p); // Prints "(sum (+ 1 (* 2 3 ) ) 8 9 )"

    evaluator e;
    expr.visit(e);
    std::cout << "=> " << e.result() << std::endl; // Prints "=> 24"
}

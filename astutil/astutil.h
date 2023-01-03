#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <optional>
#include <type_traits>
#include <variant>

namespace astutil {

namespace details {

template<typename... Ts>
using variant = std::variant<std::unique_ptr<Ts>...>;

template<typename T, typename... As>
constexpr inline auto call_if(As &&...args) {
    if constexpr (std::is_invocable_v<decltype(T{}), As...>) {
        return T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value)
        -> decltype(std::forward<T>(vis).enter(std::forward<V>(value))) const {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value)
        -> decltype(std::forward<T>(vis).exit(std::forward<V>(value))) const {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

template<typename T, typename Tp>
constexpr inline auto visit_tuple(T &&vis, Tp &&value) {
    std::apply(
        [&](auto &&...x) {
            (std::forward<decltype(x)>(x).visit(std::forward<T>(vis)), ...);
        },
        std::forward<Tp>(value));
}

struct has_children {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value)
        -> std::void_t<decltype(std::forward<V>(value).children())> const {
        visit_tuple(std::forward<T>(vis), std::forward<V>(value).children());
    }
};

template<typename T, typename = void>
struct is_optional : std::false_type {};
template<typename T>
struct is_optional<std::optional<T>> : std::true_type {};

template<typename V, typename... Ts>
constexpr inline auto visit(V &&vis, variant<Ts...> &&value) {
    return std::visit(
        [&](auto &&v) {
            using R = decltype(call_if<has_enter>(std::forward<V>(vis), *v));

            if constexpr (std::is_same_v<R, bool>) {
                if (call_if<has_enter>(std::forward<V>(vis), *v)) {
                    call_if<has_children>(std::forward<V>(vis), *v);
                }
            }
            else if constexpr (is_optional<R>::value) {
                if (auto ret = call_if<has_enter>(std::forward<V>(vis), *v)) {
                    call_if<has_children>(*ret, *v);
                }
            }
            else {
                call_if<has_enter>(std::forward<V>(vis), *v);
                call_if<has_children>(std::forward<V>(vis), *v);
            }
            return call_if<has_exit>(std::forward<V>(vis), *v);
        },
        std::forward<variant<Ts...>>(value));
}

} // namespace details

template<typename... Ts>
struct node {
    details::variant<Ts...> value;

    template<typename T>
    constexpr node(T &&v) : value{std::make_unique<T>(std::forward<T>(v))} {}

    template<typename V>
    constexpr auto visit(V &&vis) {
        details::visit(std::forward<V>(vis),
                       std::forward<details::variant<Ts...>>(value));
    }
};

} // namespace astutil

#endif // ASTUTIL_H
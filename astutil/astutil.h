#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <type_traits>
#include <variant>

namespace astutil {

namespace detail {

template<typename... Ts>
using variant = std::variant<std::unique_ptr<Ts>...>;

template<typename T, typename... As>
constexpr inline auto call_if(As &&...args) {
    if constexpr (std::is_invocable_v<decltype(std::declval<T>()), As...>) {
        T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.enter(value)) const {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.exit(value)) const {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

struct has_visit {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&value, V &&vis)
        -> decltype(value.visit(vis)) const {
        return std::forward<T>(value).visit(std::forward<V>(vis));
    }
};

template<typename V, typename... Ts>
constexpr inline auto visit(V &&vis, variant<Ts...> &&value) {
    std::visit(
        [&](auto &&v) {
            call_if<has_enter>(std::forward<V>(vis), *v);
            call_if<has_visit>(*v, std::forward<V>(vis));
            call_if<has_exit>(std::forward<V>(vis), *v);
        },
        std::forward<variant<Ts...>>(value));
}

} // namespace detail

template<typename... Ts>
struct node {
    detail::variant<Ts...> value;

    template<typename T>
    constexpr node(T &&v) : value{std::make_unique<T>(std::forward<T>(v))} {}

    template<typename V>
    constexpr auto visit(V &&vis) {
        detail::visit(std::forward<V>(vis),
                      std::forward<detail::variant<Ts...>>(value));
    }
};

} // namespace astutil

#endif // ASTUTIL_H
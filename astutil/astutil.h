#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <type_traits>
#include <variant>

namespace astutil {

namespace details {

template<typename T>
struct default_invocable : T {
    template<typename... As>
    constexpr inline auto operator()(As &&...args) const
        noexcept(std::is_nothrow_invocable_v<T, As...>)
            -> std::enable_if_t<std::is_invocable_v<T, As...>,
                                std::invoke_result_t<T, As...>> {
        return T::operator()(std::forward<As>(args)...);
    }

    template<typename... As>
    constexpr inline auto operator()(As &&...) const noexcept
        -> std::enable_if_t<!std::is_invocable_v<T, As...>> {}
};

struct invoke_enter {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).enter(std::forward<V>(value))))
            -> decltype(std::forward<T>(vis).enter(std::forward<V>(value))) {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};
constexpr inline auto enter = default_invocable<invoke_enter>{};

struct invoke_exit {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).exit(std::forward<V>(value))))
            -> decltype(std::forward<T>(vis).exit(std::forward<V>(value))) {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};
constexpr inline auto exit = default_invocable<invoke_exit>{};

template<typename T, typename V>
constexpr inline auto visit_tuple(T &&vis, V &&value) -> void {
    std::apply(
        [&](auto &&...x) {
            (std::forward<decltype(x)>(x).visit(std::forward<T>(vis)), ...);
        },
        std::forward<V>(value));
}

struct invoke_visit_children {
    template<typename T, typename V>
    constexpr inline auto operator()(T &&vis, V &&value) const
        -> decltype(std::declval<V>().children(), void(0)) {
        visit_tuple(std::forward<T>(vis), std::forward<V>(value).children());
    }
};
constexpr inline auto visit_children =
    default_invocable<invoke_visit_children>{};

template<typename V, typename T>
constexpr inline auto visit(V &&vis, T &&value) {
    return std::visit(
        [&](auto &&v) {
            enter(std::forward<V>(vis), *std::forward<decltype(v)>(v));
            visit_children(std::forward<V>(vis), *std::forward<decltype(v)>(v));
            return exit(std::forward<V>(vis), *std::forward<decltype(v)>(v));
        },
        std::forward<T>(value));
}

} // namespace details

template<typename... Ts>
struct node {
    std::variant<std::unique_ptr<Ts>...> value;

    template<typename T, typename = std::enable_if_t<
                             !std::is_same_v<node<Ts...>, std::decay_t<T>>>>
    constexpr node(T &&v) : value{std::make_unique<T>(std::forward<T>(v))} {}

    template<typename V>
    constexpr auto visit(V &&vis)
        -> decltype(details::visit(std::forward<V>(vis), value)) {
        return details::visit(std::forward<V>(vis), value);
    }

    template<typename V>
    constexpr auto visit(V &&vis) const
        -> decltype(details::visit(std::forward<V>(vis), value)) {
        return details::visit(std::forward<V>(vis), value);
    }
};

} // namespace astutil

#endif // ASTUTIL_H
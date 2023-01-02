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
    if constexpr (std::is_invocable_v<decltype(T{}), As...>) {
        return T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<
        typename T, typename V,
        typename = decltype(std::declval<T &&>().enter(std::declval<V &&>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<
        typename T, typename V,
        typename = decltype(std::declval<T &&>().exit(std::declval<V &&>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

struct has_children {
    template<typename T, typename V,
             typename Tp = decltype(std::declval<V &&>().children()),
             typename Idx = std::make_index_sequence<std::tuple_size_v<Tp>>>
    constexpr inline auto operator()(T &&vis, V &&value) const {
        visit_children(std::forward<T>(vis), std::forward<V>(value).children(),
                       Idx{});
    }

    template<typename T, typename Tp, typename I, I... ints>
    constexpr static inline auto
    visit_children(T &&vis, Tp &&children, std::integer_sequence<I, ints...>) {
        ((std::get<ints>(std::forward<Tp>(children))
              .visit(std::forward<T>(vis))),
         ...);
    }
};

template<typename V, typename... Ts>
constexpr inline auto visit(V &&vis, variant<Ts...> &&value) {
    return std::visit(
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
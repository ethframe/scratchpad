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
inline auto call_if(As &&...args) {
    if constexpr (std::is_invocable_v<decltype(std::declval<T>()), As...>) {
        T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<typename T, typename V>
    inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.enter(value)) const {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V>
    inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.exit(value)) const {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

struct has_visit {
    template<typename T, typename V>
    inline auto operator()(T &&value, V &&vis)
        -> decltype(value.visit(vis)) const {
        return std::forward<T>(value).visit(std::forward<V>(vis));
    }
};

template<typename V, typename... Ts>
inline auto visit(V &&vis, variant<Ts...> &&value) {
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

    template<typename V>
    auto visit(V &&vis) {
        detail::visit(std::forward<V>(vis),
                      std::forward<detail::variant<Ts...>>(value));
    }
};

template<typename T>
struct variant_of {
  private:
    using variant_of_t = T;

    template<typename V, typename... As>
    friend auto make_node(As &&...args);
};

template<typename V, typename... As>
auto make_node(As &&...args) {
    return typename V::variant_of_t{
        std::make_unique<V>(V{{}, std::forward<As>(args)...})};
}

} // namespace astutil

#endif // ASTUTIL_H
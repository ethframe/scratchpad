#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <type_traits>
#include <variant>

namespace astutil {

namespace detail {

template<typename T, typename... As>
inline auto call_if(As &&...args) {
    if constexpr (std::is_invocable_v<decltype(std::declval<T>()), As...>) {
        T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<typename T, typename V>
    inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.enter(std::forward<V>(value))) {
        vis.enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V>
    inline auto operator()(T &&vis, V &&value)
        -> decltype(vis.exit(std::forward<V>(value))) {
        vis.exit(std::forward<V>(value));
    }
};

struct has_visit {
    template<typename T, typename V>
    inline auto operator()(T &&value, V &&vis)
        -> decltype(value.visit(std::forward<V>(vis))) {
        value.visit(std::forward<V>(vis));
    }
};

} // namespace detail

template<typename... Ts>
struct node {
    std::variant<std::unique_ptr<Ts>...> value;

    template<typename V>
    auto visit(V &&vis) {
        std::visit(
            [&](auto &&v) {
                detail::call_if<detail::has_enter>(std::forward<V>(vis), *v);
                detail::call_if<detail::has_visit>(*v, std::forward<V>(vis));
                detail::call_if<detail::has_exit>(std::forward<V>(vis), *v);
            },
            value);
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
    using T = typename V::variant_of_t;
    return T{
        std::make_unique<V>(V{variant_of<T>{}, std::forward<As>(args)...})};
}

} // namespace astutil

#endif // ASTUTIL_H
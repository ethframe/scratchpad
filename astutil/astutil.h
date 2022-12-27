#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <variant>

namespace astutil {

namespace detail {

template<typename T, typename, typename... As>
struct select {
    static inline auto impl(As &&...) {}
};

template<typename T, typename... As>
struct select<T, std::void_t<decltype(T::call(std::declval<As>()...))>, As...> {
    static inline auto impl(As &&...args) {
        T::call(std::forward<As>(args)...);
    }
};

template<typename T, typename... As>
inline auto call_if(As &&...args) {
    select<T, void, As...>::impl(std::forward<As>(args)...);
}

struct has_enter {
    template<typename T, typename V>
    static inline auto call(T &&vis, V &&value)
        -> decltype(vis.enter(std::forward<V>(value))) {
        vis.enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V>
    static inline auto call(T &&vis, V &&value)
        -> decltype(vis.exit(std::forward<V>(value))) {
        vis.exit(std::forward<V>(value));
    }
};

struct has_visit {
    template<typename T, typename V>
    static inline auto call(T &&value, V &&vis)
        -> decltype(value.visit(std::forward<V>(vis))) {
        value.visit(std::forward<V>(vis));
    }
};

} // namespace detail

template<typename... Ts>
struct node {
    std::variant<std::unique_ptr<Ts>...> value;

    template<typename V>
    auto visit(V &&vis) -> void {
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
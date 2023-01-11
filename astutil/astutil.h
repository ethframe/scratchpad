#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <iterator>
#include <memory>
#include <type_traits>
#include <variant>
#include <vector>

namespace astutil {

namespace details {

template<typename T>
struct default_invocable : T {
    template<typename... As>
    constexpr auto operator()(As &&...args) const
        noexcept(std::is_nothrow_invocable_v<T, As...>)
            -> std::enable_if_t<std::is_invocable_v<T, As...>,
                                std::invoke_result_t<T, As...>> {
        return T::operator()(std::forward<As>(args)...);
    }

    template<typename... As>
    constexpr auto operator()(As &&...) const noexcept
        -> std::enable_if_t<!std::is_invocable_v<T, As...>> {}
};

struct invoke_enter {
    template<typename T, typename V>
    constexpr auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::declval<T>().enter(std::declval<V>())))
            -> decltype(std::declval<T>().enter(std::declval<V>())) {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};
constexpr auto enter = default_invocable<invoke_enter>{};

struct invoke_exit {
    template<typename T, typename V>
    constexpr auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::declval<T>().exit(std::declval<V>())))
            -> decltype(std::declval<T>().exit(std::declval<V>())) {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};
constexpr auto exit = default_invocable<invoke_exit>{};

template<typename T, typename V>
constexpr auto visit_tuple(T &&vis, V &&value) -> void {
    std::apply(
        [&](auto &&...x) {
            (std::forward<decltype(x)>(x).visit(std::forward<T>(vis)), ...);
        },
        std::forward<V>(value));
}

struct invoke_visit_children {
    template<typename T, typename V>
    constexpr auto operator()(T &&vis, V &&value) const
        -> decltype(std::declval<V>().children(), void(0)) {
        visit_tuple(std::forward<T>(vis), std::forward<V>(value).children());
    }
};
constexpr auto visit_children = default_invocable<invoke_visit_children>{};

template<typename V, typename T>
constexpr auto visit(V &&vis, T &&value) -> decltype(exit(
    std::declval<V>(),
    std::declval<std::variant_alternative_t<0, std::decay_t<T>>>())) {
    return std::visit(
        [&](auto &&v) {
            enter(std::forward<V>(vis), *std::forward<decltype(v)>(v));
            visit_children(std::forward<V>(vis), *std::forward<decltype(v)>(v));
            return exit(std::forward<V>(vis), *std::forward<decltype(v)>(v));
        },
        std::forward<T>(value));
}

template<typename T, typename... Ts>
constexpr auto move_to_vector(Ts &&...vs) {
    T init[]{std::forward<Ts>(vs)...};
    return std::vector<T>(std::make_move_iterator(std::begin(init)),
                          std::make_move_iterator(std::end(init)));
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
        -> decltype(details::visit(std::declval<V>(), value)) {
        return details::visit(std::forward<V>(vis), value);
    }

    template<typename V>
    constexpr auto visit(V &&vis) const
        -> decltype(details::visit(std::declval<V>(), value)) {
        return details::visit(std::forward<V>(vis), value);
    }

    struct nodes {
        using node = node<Ts...>;

        std::vector<node> values;

        template<typename... As>
        constexpr nodes(As &&...vs)
            : values{details::move_to_vector<node>(std::forward<As>(vs)...)} {}

        constexpr auto size() const noexcept(noexcept(std::size(values))) {
            return std::size(values);
        }

        template<typename V>
        constexpr auto visit(V &&vis) -> void {
            for (auto &x : values) {
                x.visit(std::forward<V>(vis));
            }
        }

        template<typename V>
        constexpr auto visit(V &&vis) const -> void {
            for (const auto &x : values) {
                x.visit(std::forward<V>(vis));
            }
        }
    };
};

} // namespace astutil

#endif // ASTUTIL_H
#ifndef ASTUTIL_H
#define ASTUTIL_H

#include <memory>
#include <optional>
#include <type_traits>
#include <variant>

namespace astutil {

namespace details {

template<typename T>
struct default_invocable : T {
    template<typename... As,
             typename = std::enable_if_t<std::is_invocable_v<T, As...>>>
    constexpr inline auto operator()(As &&...args) const
        noexcept(noexcept(T::operator()(std::forward<As>(args)...)))
            -> decltype(T::operator()(std::forward<As>(args)...)) {
        return T::operator()(std::forward<As>(args)...);
    }

    template<typename... As,
             typename = std::enable_if_t<!std::is_invocable_v<T, As...>>>
    constexpr inline auto operator()(As &&...) const noexcept -> void {}
};

struct invoke_enter {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().enter(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).enter(std::forward<V>(value)))) {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};
constexpr inline auto enter = default_invocable<invoke_enter>{};

struct invoke_exit {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().exit(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).exit(std::forward<V>(value)))) {
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
    template<typename T, typename V,
             typename = decltype(std::declval<V>().children())>
    constexpr inline auto operator()(T &&vis, V &&value) const -> void {
        visit_tuple(std::forward<T>(vis), std::forward<V>(value).children());
    }
};
constexpr inline auto visit_children =
    default_invocable<invoke_visit_children>{};

template<typename T, typename = void>
struct is_optional : std::false_type {};
template<typename T>
struct is_optional<std::optional<T>> : std::true_type {};
template<typename T>
constexpr inline auto is_optional_v = is_optional<T>::value;

template<typename V, typename T>
constexpr inline auto visit(V &&vis, T &&value) {
    return std::visit(
        [&](auto &&v) {
            using result = decltype(enter(std::forward<V>(vis),
                                          *std::forward<decltype(v)>(v)));

            if constexpr (std::is_same_v<result, bool>) {
                if (enter(std::forward<V>(vis),
                          *std::forward<decltype(v)>(v))) {
                    visit_children(std::forward<V>(vis),
                                   *std::forward<decltype(v)>(v));
                }
            }
            else if constexpr (is_optional_v<std::decay_t<result>>) {
                if (auto ret = enter(std::forward<V>(vis),
                                     *std::forward<decltype(v)>(v))) {
                    visit_children(*ret, *std::forward<decltype(v)>(v));
                }
            }
            else {
                enter(std::forward<V>(vis), *std::forward<decltype(v)>(v));
                visit_children(std::forward<V>(vis),
                               *std::forward<decltype(v)>(v));
            }
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
    constexpr auto visit(V &&vis) -> void {
        details::visit(std::forward<V>(vis), value);
    }

    template<typename V>
    constexpr auto visit(V &&vis) const -> void {
        details::visit(std::forward<V>(vis), value);
    }
};

} // namespace astutil

#endif // ASTUTIL_H
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

template<typename T, typename = void>
struct is_variant : std::false_type {};
template<typename... Ts>
struct is_variant<variant<Ts...>> : std::true_type {};
template<typename T>
constexpr inline auto is_variant_v = is_variant<T>::value;

template<typename T>
using declval_t = decltype(std::declval<T>());

template<typename, typename T, typename... As>
struct call_if_invocable_impl {
    using type = void;
    constexpr static auto is_noexcept = true;
    constexpr static inline auto impl(As &&...) noexcept -> void {}
};
template<typename T, typename... As>
struct call_if_invocable_impl<
    std::enable_if_t<std::is_invocable_v<declval_t<T>, As...>>, T, As...> {
    using type = std::invoke_result_t<declval_t<T>, As...>;
    constexpr static auto is_noexcept =
        std::is_nothrow_invocable_v<declval_t<T>, As...>;
    constexpr static inline auto impl(As &&...args) noexcept(is_noexcept)
        -> type {
        return T{}(std::forward<As>(args)...);
    }
};
template<typename T, typename... As>
constexpr inline auto call_if_invocable(As &&...args) noexcept(
    call_if_invocable_impl<void, T, As...>::is_noexcept) ->
    typename call_if_invocable_impl<void, T, As...>::type {
    return call_if_invocable_impl<void, T, As...>::impl(
        std::forward<As>(args)...);
}

struct enter {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().enter(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).enter(std::forward<V>(value)))) {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct exit {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().exit(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const
        noexcept(noexcept(std::forward<T>(vis).exit(std::forward<V>(value)))) {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

template<typename T, typename = void>
struct is_tuple : std::false_type {};
template<typename... T>
struct is_tuple<std::tuple<T...>> : std::true_type {};
template<typename T>
constexpr inline auto is_tuple_v = is_tuple<T>::value;

template<typename T, typename V,
         typename = std::enable_if_t<is_tuple_v<std::decay_t<V>>>>
constexpr inline auto visit_tuple(T &&vis, V &&value) -> void {
    std::apply(
        [&](auto &&...x) {
            (std::forward<decltype(x)>(x).visit(std::forward<T>(vis)), ...);
        },
        std::forward<V>(value));
}

struct visit_children {
    template<typename T, typename V,
             typename = decltype(std::declval<V>().children())>
    constexpr inline auto operator()(T &&vis, V &&value) const -> void {
        visit_tuple(std::forward<T>(vis), std::forward<V>(value).children());
    }
};

template<typename T, typename = void>
struct is_optional : std::false_type {};
template<typename T>
struct is_optional<std::optional<T>> : std::true_type {};
template<typename T>
constexpr inline auto is_optional_v = is_optional<T>::value;

template<typename V, typename T,
         typename = std::enable_if_t<is_variant_v<std::decay_t<T>>>>
constexpr inline auto visit(V &&vis, T &&value) {
    return std::visit(
        [&](auto &&v) {
            using R =
                decltype(call_if_invocable<enter>(std::forward<V>(vis), *v));

            if constexpr (std::is_same_v<R, bool>) {
                if (call_if_invocable<enter>(std::forward<V>(vis), *v)) {
                    call_if_invocable<visit_children>(std::forward<V>(vis), *v);
                }
            }
            else if constexpr (is_optional_v<R>) {
                if (auto ret =
                        call_if_invocable<enter>(std::forward<V>(vis), *v)) {
                    call_if_invocable<visit_children>(*ret, *v);
                }
            }
            else {
                call_if_invocable<enter>(std::forward<V>(vis), *v);
                call_if_invocable<visit_children>(std::forward<V>(vis), *v);
            }
            return call_if_invocable<exit>(std::forward<V>(vis), *v);
        },
        std::forward<T>(value));
}

} // namespace details

template<typename... Ts>
struct node {
    details::variant<Ts...> value;

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
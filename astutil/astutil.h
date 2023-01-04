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

template<typename, typename T, typename... As>
struct call_if_result {
    using type = void;
};
template<typename T, typename... As>
struct call_if_result<std::void_t<std::invoke_result_t<decltype(T{}), As...>>,
                      T, As...> {
    using type = std::invoke_result_t<decltype(T{}), As...>;
};
template<typename T, typename... As>
using call_if_result_t = typename call_if_result<T, As...>::type;

template<typename T, typename... As>
constexpr inline auto call_if(As &&...args) -> call_if_result_t<T, As...> {
    if constexpr (std::is_invocable_v<decltype(T{}), As...>) {
        return T{}(std::forward<As>(args)...);
    }
}

struct has_enter {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().enter(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const {
        return std::forward<T>(vis).enter(std::forward<V>(value));
    }
};

struct has_exit {
    template<typename T, typename V,
             typename = decltype(std::declval<T>().exit(std::declval<V>()))>
    constexpr inline auto operator()(T &&vis, V &&value) const {
        return std::forward<T>(vis).exit(std::forward<V>(value));
    }
};

template<typename T, typename = void>
struct is_tuple : std::false_type {};
template<typename... T>
struct is_tuple<std::tuple<T...>> : std::true_type {};

template<typename T, typename V,
         typename = std::enable_if_t<
             is_tuple<std::remove_cv_t<std::remove_reference_t<V>>>::value>>
constexpr inline auto visit_tuple(T &&vis, V &&value) -> void {
    std::apply(
        [&](auto &&...x) {
            (std::forward<decltype(x)>(x).visit(std::forward<T>(vis)), ...);
        },
        std::forward<V>(value));
}

struct has_children {
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

template<typename V, typename T,
         typename = std::enable_if_t<
             is_variant<std::remove_cv_t<std::remove_reference_t<T>>>::value>>
constexpr inline auto visit(V &&vis, T &&value) {
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
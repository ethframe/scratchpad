from absal.absal import App, Lam, Op, Val, Var, dup, run


def add(lhs: int, rhs: int) -> int:
    return lhs + rhs


def test_simple() -> None:
    x = Var()
    x1, x2 = dup(x)

    f = Lam(x, Op(add, x1, x2))
    f1, f2 = dup(f)

    term = Op(add, App(f1, Val(1)), App(f2, Val(2)))

    out = run(term)
    assert isinstance(out, Val)
    assert out.val == 6


def test_high_order() -> None:
    f = Var()
    f1, f2 = dup(f)
    x = Var()
    g = Lam(f, Lam(x, App(f1, App(f2, x))))

    hf = Var()
    hf1, hf2 = dup(hf)
    hx = Var()
    h = Lam(hf, Lam(hx, App(hf1, App(hf2, hx))))

    gh = App(g, h)

    y = Var()
    term = App(App(gh, Lam(y, Op(add, y, Val(1)))), Val(1))

    out = run(term)
    assert isinstance(out, Val)
    assert out.val == 5

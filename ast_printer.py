from expr import Expr, Binary, Unary, Grouping, Literal
from functools import singledispatch


def parenthesize(name: str, *parts: str) -> str:
    return f"({name}" + "".join(f" {p}" for p in parts) + ")"


@singledispatch
def print_ast(expr: Expr) -> str:
    raise TypeError(f"No printer for {type(expr).__name__}")


@print_ast.register
def _(expr: Binary) -> str:
    return parenthesize(
        expr.operator.lexeme, print_ast(expr.left), print_ast(expr.right)
    )


@print_ast.register
def _(expr: Unary) -> str:
    return parenthesize(expr.operator.lexeme, print_ast(expr.right))


@print_ast.register
def _(expr: Grouping) -> str:
    return parenthesize("group", print_ast(expr.expression))


@print_ast.register
def _(expr: Literal) -> str:
    if expr.value == None:
        return "nil"
    return str(expr.value)

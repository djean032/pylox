from __future__ import annotations

from tokens import Token


class Expr: ...

class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None: ...

class Unary(Expr):
    operator: Token
    right: Expr
    def __init__(self, operator: Token, right: Expr) -> None: ...

class Grouping(Expr):
    expression: Expr
    def __init__(self, expression: Expr) -> None: ...

class Literal(Expr):
    value: object
    def __init__(self, value: object) -> None: ...

class Variable(Expr):
    name: Token
    def __init__(self, name: Token) -> None: ...

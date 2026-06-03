from __future__ import annotations

from tokens import Token


class Expr: ...

class Assign(Expr):
    name: Token
    value: Expr
    def __init__(self, name: Token, value: Expr) -> None: ...

class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None: ...

class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]
    def __init__(self, callee: Expr, paren: Token, arguments: list[Expr]) -> None: ...

class Get(Expr):
    object: Expr
    name: Token
    def __init__(self, object: Expr, name: Token) -> None: ...

class Grouping(Expr):
    expression: Expr
    def __init__(self, expression: Expr) -> None: ...

class Literal(Expr):
    value: object
    def __init__(self, value: object) -> None: ...

class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None: ...

class Set(Expr):
    object: Expr
    name: Token
    value: Expr
    def __init__(self, object: Expr, name: Token, value: Expr) -> None: ...

class Super(Expr):
    keyword: Token
    method: Token
    def __init__(self, keyword: Token, method: Token) -> None: ...

class This(Expr):
    keyword: Token
    def __init__(self, keyword: Token) -> None: ...

class Unary(Expr):
    operator: Token
    right: Expr
    def __init__(self, operator: Token, right: Expr) -> None: ...

class Variable(Expr):
    name: Token
    def __init__(self, name: Token) -> None: ...

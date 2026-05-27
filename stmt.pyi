from __future__ import annotations

from tokens import Token
from expr import Expr


class Stmt: ...

class Expression(Stmt):
    expr: Expr
    def __init__(self, expr: Expr) -> None: ...

class Print(Stmt):
    expr: Expr
    def __init__(self, expr: Expr) -> None: ...

class Var(Stmt):
    name: Token
    initializer: Expr | None
    def __init__(self, name: Token, initializer: Expr | None) -> None: ...

class Block(Stmt):
    statements: list[Stmt]
    def __init__(self, statements: list[Stmt]) -> None: ...

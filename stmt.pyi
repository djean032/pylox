from __future__ import annotations

from tokens import Token
from expr import Expr


class Stmt: ...

class Block(Stmt):
    statements: list[Stmt]
    def __init__(self, statements: list[Stmt]) -> None: ...

class Class(Stmt):
    name: Token
    methods: list[Function]
    def __init__(self, name: Token, methods: list[Function]) -> None: ...

class Expression(Stmt):
    expr: Expr
    def __init__(self, expr: Expr) -> None: ...

class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]
    def __init__(self, name: Token, params: list[Token], body: list[Stmt]) -> None: ...

class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Stmt | None) -> None: ...

class Print(Stmt):
    expr: Expr
    def __init__(self, expr: Expr) -> None: ...

class Return(Stmt):
    keyword: Token
    value: Expr | None
    def __init__(self, keyword: Token, value: Expr | None) -> None: ...

class Var(Stmt):
    name: Token
    initializer: Expr | None
    def __init__(self, name: Token, initializer: Expr | None) -> None: ...

class While(Stmt):
    condition: Expr
    body: Stmt
    def __init__(self, condition: Expr, body: Stmt) -> None: ...

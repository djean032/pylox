from __future__ import annotations

from tokens import Token
from expr import Expr


class Stmt: ...

class Expression(Stmt):
    expr: Expr

class Print(Stmt):
    expr: Expr

class Var(Stmt):
    name: Token
    initializer: Expr

from interpreter import Interpreter
from stmt import Block, Stmt, Var, Expression, Print, If, While, Function, Return
from tokens import Token
from expr import (
    Expr,
    Binary,
    Unary,
    Variable,
    Call,
    Grouping,
    Literal,
    Logical,
    Assign,
    Get,
)
from loxerror import LoxErrors

from functools import singledispatch
from enum import Enum, auto


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()


class Resolver:
    def __init__(self, interpreter: Interpreter) -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.had_error = False

    def resolve_all(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, statement: Stmt) -> None:
        _resolve_stmt(self, statement)

    def resolve_expr(self, expr: Expr) -> None:
        _resolve_expr(self, expr)

    def begin_scope(self) -> None:
        self.scopes.append({})

    def end_scope(self) -> None:
        self.scopes.pop()

    def declare(self, name: Token) -> None:
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope:
            LoxErrors.report(
                name.line,
                f" at '{name.lexeme}'",
                "Already a variable with this name in this scope.",
            )
            self.had_error = True
        scope[name.lexeme] = False

    def define(self, name: Token) -> None:
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: Expr, name: Token) -> None:
        for depth, scope in enumerate(reversed(self.scopes)):
            if name.lexeme in scope:
                self.interpreter.resolve(expr, depth)

    def visit_function(self, stmt: Function) -> None:
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt, FunctionType.FUNCTION)

    def resolve_function(self, function: Function, function_type: FunctionType) -> None:
        enclosing_function = self.current_function
        self.current_function = function_type
        self.begin_scope()
        try:
            for param in function.params:
                self.declare(param)
                self.define(param)
            self.resolve_all(function.body)
        finally:
            self.end_scope()
            self.current_function = enclosing_function


@singledispatch
def _resolve_stmt(stmt: Stmt, resolver: Resolver) -> None:
    _ = resolver
    raise TypeError(f"No stmt resolver for {type(stmt).__name__}")


@_resolve_stmt.register
def _(stmt: Block, resolver: Resolver) -> None:
    resolver.begin_scope()
    try:
        resolver.resolve_all(stmt.statements)
    finally:
        resolver.end_scope()


@_resolve_stmt.register
def _(stmt: Var, resolver: Resolver) -> None:
    resolver.declare(stmt.name)
    if stmt.initializer is not None:
        resolver.resolve_expr(stmt.initializer)
    resolver.define(stmt.name)


@_resolve_stmt.register
def _(stmt: Expression, resolver: Resolver) -> None:
    resolver.resolve_expr(stmt.expr)


@_resolve_stmt.register
def _(stmt: Print, resolver: Resolver) -> None:
    resolver.resolve_expr(stmt.expr)


@_resolve_stmt.register
def _(stmt: If, resolver: Resolver) -> None:
    resolver.resolve_expr(stmt.condition)
    resolver.resolve_stmt(stmt.then_branch)
    if stmt.else_branch is not None:
        resolver.resolve_stmt(stmt.else_branch)


@_resolve_stmt.register
def _(stmt: While, resolver: Resolver) -> None:
    resolver.resolve_expr(stmt.condition)
    resolver.resolve_stmt(stmt.body)


@_resolve_stmt.register
def _(stmt: Function, resolver: Resolver) -> None:
    resolver.visit_function(stmt)


@_resolve_stmt.register
def _(stmt: Return, resolver: Resolver) -> None:
    if resolver.current_function == FunctionType.NONE:
        LoxErrors.report(stmt.keyword.line, "", "Can't return from top-level code.")
        resolver.had_error = True
    if stmt.value is not None:
        resolver.resolve_expr(stmt.value)


@singledispatch
def _resolve_expr(expr: Expr, resolver: Resolver) -> None:
    _ = resolver
    raise TypeError(f"No expr resolver for {type(expr).__name__}")


@_resolve_expr.register
def _(expr: Binary, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.left)
    resolver.resolve_expr(expr.right)


@_resolve_expr.register
def _(expr: Unary, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.right)


@_resolve_expr.register
def _(expr: Logical, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.left)
    resolver.resolve_expr(expr.right)


@_resolve_expr.register
def _(expr: Literal, resolver: Resolver) -> None:
    _ = expr
    _ = resolver
    return


@_resolve_expr.register
def _(expr: Call, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.callee)

    for arg in expr.arguments:
        resolver.resolve_expr(arg)


@_resolve_expr.register
def _(expr: Get, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.object)


@_resolve_expr.register
def _(expr: Variable, resolver: Resolver) -> None:
    if resolver.scopes and resolver.scopes[-1].get(expr.name.lexeme) is False:
        pass
    resolver.resolve_local(expr, expr.name)


@_resolve_expr.register
def _(expr: Grouping, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.expression)


@_resolve_expr.register
def _(expr: Assign, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.value)
    resolver.resolve_local(expr, expr.name)

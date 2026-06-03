from typing import TYPE_CHECKING
from stmt import Block, Stmt, Var, Expression, Print, If, While, Function, Return, Class
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
    Set,
    This,
)
from loxerror import LoxErrors

from functools import singledispatch
from enum import Enum, auto

if TYPE_CHECKING:
    from interpreter import Interpreter


class FunctionType(Enum):
    NONE = auto()
    FUNCTION = auto()
    INITIALIZER = auto()
    METHOD = auto()


class ClassType(Enum):
    NONE = auto()
    CLASS = auto()
    SUBCLASS = auto()


class Resolver:
    def __init__(self, interpreter: "Interpreter") -> None:
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []
        self.current_function = FunctionType.NONE
        self.current_class = ClassType.NONE
        self.had_error = False

    def resolve_all(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, statement: Stmt) -> None:
        _resolve_stmt(statement, self)

    def resolve_expr(self, expr: Expr) -> None:
        _resolve_expr(expr, self)

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
        if resolver.current_function == FunctionType.INITIALIZER:
            LoxErrors.report(
                stmt.keyword.line,
                f" at '{stmt.keyword.lexeme}'",
                "Cannot return a value from an initializer.",
            )
            resolver.had_error = True
        resolver.resolve_expr(stmt.value)


@_resolve_stmt.register
def _(stmt: Class, resolver: Resolver) -> None:
    enclosing_class: ClassType = resolver.current_class
    resolver.current_class = ClassType.CLASS
    resolver.declare(stmt.name)
    resolver.define(stmt.name)

    if stmt.superclass is not None and stmt.name.lexeme == stmt.superclass.name.lexeme:
        LoxErrors.report(
            stmt.superclass.name.line,
            f" at '{stmt.superclass.name.lexeme}'",
            "A class cannot inherit from itself.",
        )
        resolver.had_error = True
    if stmt.superclass is not None:
        resolver.begin_scope()
        resolver.scopes[-1]["super"] = True
        resolver.current_class = ClassType.SUBCLASS
        resolver.resolve_expr(stmt.superclass)

    resolver.begin_scope()
    try:
        resolver.scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration: FunctionType = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER
            resolver.resolve_function(method, declaration)

    finally:
        resolver.end_scope()
        resolver.current_class = enclosing_class


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
def _(expr: Set, resolver: Resolver) -> None:
    resolver.resolve_expr(expr.value)
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


@_resolve_expr.register
def _(expr: This, resolver: Resolver) -> None:
    if resolver.current_class is ClassType.NONE:
        LoxErrors.report(
            expr.keyword.line,
            f" at '{expr.keyword.lexeme}'",
            'Cannot use "this" outside of a class.',
        )
        resolver.had_error = True
        return
    resolver.resolve_local(expr, expr.keyword)

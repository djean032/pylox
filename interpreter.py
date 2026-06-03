from functools import singledispatch
from expr import (
    Expr,
    Assign,
    Binary,
    Unary,
    Grouping,
    Literal,
    Variable,
    Logical,
    Call,
    Get,
    Set,
    This,
)
from stmt import Return, Stmt, Expression, Print, Var, Block, If, While, Function, Class
from environment import Environment
from resolver import Resolver
from loxerror import LoxRuntimeError
from loxcallable import LoxCallable
from loxfunction import LoxFunction
from loxinstance import LoxInstance
from loxclass import LoxClass
from return_signal import ReturnSignal
from values import LoxValue
from time import time
from typing import Tuple, List

from tokens import Token, TokenType


class Clock:
    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: list[LoxValue]) -> float:
        _ = interpreter
        _ = arguments
        return time()

    def __str__(self) -> str:
        return "<native fn>"


class Interpreter:

    def __init__(self):
        self.globals: Environment = Environment()
        self.environment: Environment = self.globals
        self.resolver: Resolver = Resolver(self)
        self.locals: dict[Expr, int] = {}

        self.globals.define("clock", Clock())

    def interpret(self, statements: list[Stmt]) -> None:
        for statement in statements:
            self.execute(statement)

    def stringify(self, value: LoxValue) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float):
            text = str(value)
            return text[:-2] if text.endswith(".0") else text
        return str(value)

    def evaluate(self, expr: Expr) -> LoxValue:
        return eval(expr, self)

    def execute(self, stmt: Stmt) -> None:
        exec(stmt, self)

    def resolve(self, expr: Expr, depth: int) -> None:
        self.locals[expr] = depth

    def visit_expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expr)

    def visit_class(self, stmt: Class) -> None:
        superclass: LoxClass | None = None
        if stmt.superclass is not None:
            value: LoxValue = self.evaluate(stmt.superclass)
            if not isinstance(value, LoxClass):
                raise LoxRuntimeError(
                    stmt.superclass.name, "Superclass must be a class"
                )
            superclass = value

        self.environment.define(stmt.name.lexeme, None)
        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            function: LoxFunction = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
            methods[method.name.lexeme] = function

        klass: LoxClass = LoxClass(stmt.name.lexeme, superclass, methods)
        self.environment.assign(stmt.name, klass)

    def visit_function(self, stmt: Function) -> None:
        function: LoxFunction = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visit_return(self, stmt: Return) -> None:
        value: LoxValue = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise ReturnSignal(value)

    def visit_print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))

    def visit_var(self, stmt: Var) -> None:
        value: LoxValue | None = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visit_block(self, stmt: Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))
        return None

    def visit_if(self, stmt: If) -> None:
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_while(self, stmt: While) -> None:
        while self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)
        return None

    def execute_block(self, statements: list[Stmt], environment: Environment) -> None:
        previous: Environment = self.environment
        try:
            self.environment = environment

            for statement in statements:
                self.execute(statement)

        finally:
            self.environment = previous

    def visit_assign(self, expr: Assign) -> LoxValue:
        value: LoxValue = self.evaluate(expr.value)
        distance: int | None = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_get(self, expr: Get) -> LoxValue:
        object: LoxValue = self.evaluate(expr.object)
        if isinstance(object, LoxInstance):
            return object.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

    def visit_set(self, expr: Set) -> LoxValue:
        object: LoxValue = self.evaluate(expr.object)
        if not isinstance(object, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value: LoxValue = self.evaluate(expr.value)
        object.set(expr.name, value)
        return value

    def visit_this(self, expr: This) -> LoxValue:
        return self.lookup_variable(expr.keyword, expr)

    def visit_logical(self, expr: Logical) -> LoxValue:
        left: LoxValue = self.evaluate(expr.left)

        if expr.operator.token_type == TokenType.OR:
            if self.is_truthy(left):
                return left
            else:
                if not self.is_truthy(left):
                    return left
        return self.evaluate(expr.right)

    def visit_call(self, expr: Call) -> LoxValue:
        callee: LoxValue = self.evaluate(expr.callee)
        arguments: list[LoxValue] = [
            self.evaluate(argument) for argument in expr.arguments
        ]
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visit_binary(self, expr: Binary) -> LoxValue:
        right: LoxValue = self.evaluate(expr.right)
        left: LoxValue = self.evaluate(expr.left)

        match expr.operator.token_type:
            case TokenType.MINUS:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num - right_num
            case TokenType.SLASH:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num / right_num
            case TokenType.STAR:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num * right_num
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                elif isinstance(left, str) and isinstance(right, str):
                    return left + right
                else:
                    raise LoxRuntimeError(
                        expr.operator,
                        f"'{expr.operator.lexeme}' requires the operands to be two numbers or two strings.",
                    )
            case TokenType.GREATER:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num > right_num
            case TokenType.GREATER_EQUAL:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num >= right_num
            case TokenType.LESS:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num < right_num
            case TokenType.LESS_EQUAL:
                left_num, right_num = self.check_num(expr.operator, left, right)
                return left_num <= right_num
            case TokenType.EQUAL_EQUAL:
                return self.is_equal(left, right)
            case TokenType.BANG_EQUAL:
                return not self.is_equal(left, right)
            case _:
                raise LoxRuntimeError(
                    expr.operator, f"Unknown binary operator '{expr.operator.lexeme}'."
                )

    def visit_unary(self, expr: Unary) -> LoxValue:
        right: LoxValue = self.evaluate(expr.right)

        match expr.operator.token_type:
            case TokenType.MINUS:
                (number,) = self.check_num(expr.operator, right)
                return -number
            case TokenType.BANG:
                return not self.is_truthy(right)
            case _:
                raise LoxRuntimeError(
                    expr.operator, f"Unknown unary operator '{expr.operator.lexeme}'."
                )

    def visit_grouping(self, expr: Grouping) -> LoxValue:
        return self.evaluate(expr.expression)

    def visit_literal(self, expr: Literal) -> LoxValue:
        value = expr.value

        if isinstance(value, int):
            return float(value)
        if isinstance(value, (float, str, bool)) or value is None:
            return value

        raise TypeError(f"Unsupported literal type value {type(value).__name__}")

    def visit_variable(self, expr: Variable) -> LoxValue:
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: Expr) -> LoxValue:
        distance: int | None = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

    def check_num(self, operator: Token, *operands: LoxValue) -> Tuple[float, ...]:
        numbers: List[float] = []
        for operand in operands:
            if not isinstance(operand, float):
                raise LoxRuntimeError(operator, "Operands must be numbers.")
            numbers.append(float(operand))
        return tuple(numbers)

    def is_truthy(self, operand: LoxValue) -> bool:
        if operand is None:
            return False
        if isinstance(operand, bool):
            return operand
        return True

    # TODO: I should make this more robust...
    def is_equal(self, a: LoxValue, b: LoxValue) -> bool:
        if a is None and b is None:
            return True
        if a is None:
            return False
        return a == b


@singledispatch
def eval(expr: Expr, interp: "Interpreter") -> LoxValue:
    _ = interp
    raise TypeError(f"No visit handler for {type(expr).__name__}")


@eval.register
def _(expr: Binary, interp: "Interpreter") -> LoxValue:
    return interp.visit_binary(expr)


@eval.register
def _(expr: Unary, interp: "Interpreter") -> LoxValue:
    return interp.visit_unary(expr)


@eval.register
def _(expr: Grouping, interp: "Interpreter") -> LoxValue:
    return interp.visit_grouping(expr)


@eval.register
def _(expr: Literal, interp: "Interpreter") -> LoxValue:
    return interp.visit_literal(expr)


@eval.register
def _(expr: Variable, interp: "Interpreter") -> LoxValue:
    return interp.visit_variable(expr)


@eval.register
def _(expr: Logical, interp: "Interpreter") -> LoxValue:
    return interp.visit_logical(expr)


@eval.register
def _(expr: Call, interp: "Interpreter") -> LoxValue:
    return interp.visit_call(expr)


@eval.register
def _(expr: Assign, interp: "Interpreter") -> LoxValue:
    return interp.visit_assign(expr)


@eval.register
def _(expr: Get, interp: "Interpreter") -> LoxValue:
    return interp.visit_get(expr)


@eval.register
def _(expr: This, interp: "Interpreter") -> LoxValue:
    return interp.visit_this(expr)


@eval.register
def _(expr: Set, interp: "Interpreter") -> LoxValue:
    return interp.visit_set(expr)


@singledispatch
def exec(stmt: Stmt, interp: "Interpreter") -> None:
    _ = interp
    raise TypeError(f"No execute handler for {type(stmt).__name__}")


@exec.register
def _(stmt: Expression, interp: "Interpreter") -> None:
    interp.visit_expression(stmt)


@exec.register
def _(stmt: Print, interp: "Interpreter") -> None:
    interp.visit_print(stmt)


@exec.register
def _(stmt: Var, interp: "Interpreter") -> None:
    interp.visit_var(stmt)


@exec.register
def _(stmt: Block, interp: "Interpreter") -> None:
    interp.visit_block(stmt)


@exec.register
def _(stmt: If, interp: "Interpreter") -> None:
    interp.visit_if(stmt)


@exec.register
def _(stmt: While, interp: "Interpreter") -> None:
    interp.visit_while(stmt)


@exec.register
def _(stmt: Function, interp: "Interpreter") -> None:
    interp.visit_function(stmt)


@exec.register
def _(stmt: Return, interp: "Interpreter") -> None:
    interp.visit_return(stmt)


@exec.register
def _(stmt: Class, interp: "Interpreter") -> None:
    interp.visit_class(stmt)

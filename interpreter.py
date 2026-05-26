from functools import singledispatch
from expr import Expr, Binary, Unary, Grouping, Literal
from stmt import Stmt, Expression, Print, Var
from loxerror import LoxRuntimeError, LoxErrors
from typing import TypeAlias, Tuple, List

from tokens import Token, TokenType


LoxValue: TypeAlias = float | str | bool | None


class Interpreter:

    def interpret(self, expr: Expr) -> None:
        try:
            value = self.evaluate(expr)
            print(self.stringify(value))
        except LoxRuntimeError as err:
            LoxErrors.report(
                err.operator.line, f" at '{err.operator.lexeme}'", err.message
            )

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

    def visit_expression(self, stmt: Expression) -> None:
        self.evaluate(stmt.expr)

    def visit_print(self, stmt: Print) -> None:
        value = self.evaluate(stmt.expr)
        print(self.stringify(value))

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

@singledispatch
def exec(stmt: Stmt, interp: "Interpreter") -> None:
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

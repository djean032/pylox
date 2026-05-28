from __future__ import annotations

from typing import TYPE_CHECKING

from loxcallable import LoxCallable
from environment import Environment
from return_signal import ReturnSignal
from stmt import Function
from values import LoxValue

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function, closure: Environment) -> None:
        self.declaration = declaration
        self.closure = closure

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: list[LoxValue]) -> LoxValue:
        environment: Environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnSignal as signal:
            return signal.value
        return None

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

from __future__ import annotations

from typing import TYPE_CHECKING

from loxcallable import LoxCallable
from environment import Environment
from return_signal import ReturnSignal
from stmt import Function
from values import LoxValue

if TYPE_CHECKING:
    from interpreter import Interpreter
    from loxinstance import LoxInstance


class LoxFunction(LoxCallable):
    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool = False
    ) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interpreter: "Interpreter", arguments: list[LoxValue]) -> LoxValue:
        environment: Environment = Environment(self.closure)
        for i, param in enumerate(self.declaration.params):
            environment.define(param.lexeme, arguments[i])

        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnSignal as signal:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return signal.value
        if self.is_initializer:
            return self.closure.get_at(0, "this")
        return None

    def bind(self, instance: "LoxInstance") -> LoxFunction:
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"

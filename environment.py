from typing import Dict
from loxerror import LoxRuntimeError
from tokens import Token
from values import LoxValue


class Environment:
    def __init__(self, enclosing: "Environment | None" = None):
        self.values: Dict[str, LoxValue] = {}
        self.enclosing = enclosing

    def get(self, name: Token) -> LoxValue:
        if name.lexeme in self.values:
            return self.values.get(name.lexeme)
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f'Undefined variable "{name.lexeme}".')

    def define(self, name: str, value: LoxValue) -> None:
        self.values[name] = value

    def assign(self, name: Token, value: LoxValue) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return None
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return None
        raise LoxRuntimeError(name, f'Undefined variable "{name.lexeme}".')

    def get_at(self, distance: int, name: str) -> LoxValue:
        return self.ancestor(distance).values[name]

    def ancestor(self, distance: int) -> "Environment":
        environment: Environment = self
        for _ in range(distance):
            if environment.enclosing is None:
                raise RuntimeError("Missing enclosing environment.")
            environment = environment.enclosing
        return environment

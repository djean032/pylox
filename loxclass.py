from __future__ import annotations
from typing import TYPE_CHECKING
from loxinstance import LoxInstance
from loxcallable import LoxCallable
from values import LoxValue

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name = name

    def arity(self) -> int:
        return 0

    def call(self, interpreter: "Interpreter", arguments: list[LoxValue]) -> LoxValue:
        _ = interpreter
        _ = arguments
        instance: LoxInstance = LoxInstance(self)
        return instance

    def __str__(self) -> str:
        return self.name

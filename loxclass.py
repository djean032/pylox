from __future__ import annotations
from typing import TYPE_CHECKING
from loxcallable import LoxCallable

if TYPE_CHECKING:
    from interpreter import Interpreter


class LoxClass(LoxCallable):
    def __init__(self, name: str):
        self.name = name

    def arity(self) -> int:
        return 0

    def call(self, interp: "Interpreter", arguments: list[LoxValue]) -> LoxValue:
        instance: LoxInstance(self)
        return instance

    def __str__(self) -> str:
        return self.name

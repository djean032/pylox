# lox_callable.py
from __future__ import annotations
from typing import Protocol, runtime_checkable, TYPE_CHECKING
from values import LoxValue

if TYPE_CHECKING:
    from interpreter import Interpreter


@runtime_checkable
class LoxCallable(Protocol):
    def arity(self) -> int: ...

    def call(
        self, interpreter: "Interpreter", arguments: list[LoxValue]
    ) -> LoxValue: ...

# lox_callable.py
from __future__ import annotations
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING
if TYPE_CHECKING:
    from interpreter import Interpreter

@runtime_checkable
class LoxCallable(Protocol):
    def arity(self) -> int:
        ...

    def call(self, interpreter: "Interpreter", arguments: list[Any]) -> Any:
        ...

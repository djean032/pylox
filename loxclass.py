from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from values import LoxValue
from loxcallable import LoxCallable

if TYPE_CHECKING:
    from interpreter import Interpreter
    from loxfunction import LoxFunction


class LoxClass(LoxCallable):
    def __init__(
        self,
        name: str,
        superclass: Optional[LoxClass] = None,
        methods: Optional[dict[str, "LoxFunction"]] = None,
    ):
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def arity(self) -> int:
        initializer: "LoxFunction | None" = self.find_method("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interpreter: "Interpreter", arguments: list[LoxValue]) -> LoxValue:
        from loxinstance import LoxInstance

        _ = interpreter
        _ = arguments
        instance = LoxInstance(self)
        initializer: "LoxFunction | None" = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments)
        return instance

    def find_method(self, name: str) -> Optional["LoxFunction"]:
        if self.methods is not None and name in self.methods:
            return self.methods[name]
        if self.superclass is not None:
            return self.superclass.find_method(name)
        return None

    def __str__(self) -> str:
        return self.name

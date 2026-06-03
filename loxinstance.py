from loxclass import LoxClass
from loxerror import LoxRuntimeError
from loxfunction import LoxFunction
from values import LoxValue
from tokens import Token


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields: dict[str, LoxValue] = {}

    def get(self, name: Token) -> LoxValue:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method: LoxFunction | None = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRuntimeError(name, f'Undefined property "{name.lexeme}".')

    def set(self, name: Token, value: LoxValue) -> None:
        self.fields[name.lexeme] = value

    def __str__(self) -> str:
        return f"{self.klass.name} instance"

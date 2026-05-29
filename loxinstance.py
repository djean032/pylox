from loxclass import LoxClass
from loxerror import LoxRuntimeError
from values import LoxValue
from tokens import Token


class LoxInstance:
    def __init__(self, klass: LoxClass) -> None:
        self.klass = klass
        self.fields: dict[str, LoxValue] = {}

    def get(self, name: Token) -> LoxValue:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        raise LoxRuntimeError(name, f'Undefined property "{name.lexeme}".')

    def __str__(self) -> str:
        return f"{self.klass.name} instance"

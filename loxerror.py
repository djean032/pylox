import sys
from tokens import Token


class LoxErrors(Exception):

    @staticmethod
    def report(line: int, where: str, message: str) -> None:
        print(f"[Line {line}] Error{where}: {message}", file=sys.stderr)

    def __str__(self) -> str:
        return "Lox error"


class LoxScanError(LoxErrors):
    def __init__(self, line: int, message: str):
        super().__init__(message)
        self.line = line
        self.message = message

    def __str__(self) -> str:
        return f"[Line {self.line}] Error: {self.message}"


class LoxParseError(LoxErrors):
    def __init__(self, token, message: str):
        super().__init__(message)
        self.token = token
        self.message = message

    def __str__(self) -> str:
        if self.token.token_type.name == "EOF":
            where = " at end"
        else:
            where = f" at '{self.token.lexeme}'"
        return f"[Line {self.token.line}] Error{where}: {self.message}"


class LoxRuntimeError(RuntimeError):
    def __init__(self, operator: Token, message: str) -> None:
        super().__init__(message)
        self.operator = operator
        self.message = message

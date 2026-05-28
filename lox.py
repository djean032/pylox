from pathlib import Path
from loxerror import LoxScanError, LoxErrors, LoxRuntimeError
from scanner import Scanner
from stmt import Stmt
from parser import Parser
from tokens import TokenType
from interpreter import Interpreter


class Lox:
    def __init__(self):
        self.had_error = False

    def main(self, args: list[str]) -> None:
        if len(args) > 1:
            print("Usage: pylox [script]")
            exit(64)
        elif len(args) == 1:
            self.run_file(args[0])
        else:
            self.run_prompt()

    def run_file(self, filepath: str) -> None:
        source = Path(filepath).read_text(encoding="utf-8")
        self.run(source)
        if self.had_error:
            exit(65)

    def run_prompt(self) -> None:
        while True:
            print("> ", end="")
            line = input()
            if line == "":
                break
            self.run(line)
            self.had_error = False

    def run(self, source: str) -> None:
        try:
            scanner = Scanner(source)
            scanner.scan_tokens()
        except LoxScanError as err:
            LoxErrors.report(err.line, "", err.message)
            self.had_error = True
            return

        parser = Parser(scanner.tokens)
        statements: list[Stmt] = parser.parse()
        if parser.had_error:
            self.had_error = True
            return
        try:
            Interpreter().interpret(statements)
        except LoxRuntimeError as err:
            where = (
                " at end"
                if err.operator.token_type == TokenType.EOF
                else f" at '{err.operator.lexeme}'"
            )
            LoxErrors.report(err.operator.line, where, err.message)
            self.had_error = True
            return

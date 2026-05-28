import pytest

from ast_printer import print_ast
from parser import Parser
from scanner import Scanner
from stmt import Expression


def parse_to_ast(source: str) -> str | None:
    scanner = Scanner(source)
    scanner.scan_tokens()
    parser = Parser(scanner.tokens)
    statements = parser.parse()
    if parser.had_error or not statements:
        return None
    stmt = statements[0]
    if not isinstance(stmt, Expression):
        return None
    return print_ast(stmt.expr)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1 + 2 * 3;", "(+ 1.0 (* 2.0 3.0))"),
        ("(1 + 2) * 3;", "(* (group (+ 1.0 2.0)) 3.0)"),
        ("-123;", "(- 123.0)"),
        ("!-true;", "(! (- True))"),
        ("3 > 2 == true;", "(== (> 3.0 2.0) True)"),
        ("nil == nil;", "(== nil nil)"),
        ('"hi";', "hi"),
        ("1 + (2 * (3 - 4));", "(+ 1.0 (group (* 2.0 (group (- 3.0 4.0)))))"),
    ],
)
def test_expression_ast_output(source: str, expected: str) -> None:
    actual = parse_to_ast(source)
    print(f"AST for {source!r}: {actual}")
    assert actual == expected

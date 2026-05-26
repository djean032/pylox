import pytest

from loxerror import LoxScanError
from parser import Parser
from scanner import Scanner


@pytest.mark.parametrize("source", ["(1 + 2", "1 + * 2", "true =="])
def test_invalid_parser_input_returns_none(source: str, capsys) -> None:
    scanner = Scanner(source)
    scanner.scan_tokens()

    expr = Parser(scanner.tokens).parse()

    out = capsys.readouterr()
    assert expr is None
    assert "Error" in out.err


@pytest.mark.parametrize("source", ["@", '"unterminated'])
def test_invalid_scanner_input_raises(source: str) -> None:
    with pytest.raises(LoxScanError):
        Scanner(source).scan_tokens()

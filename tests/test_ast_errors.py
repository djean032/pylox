import pytest

from loxerror import LoxScanError
from parser import Parser
from scanner import Scanner


@pytest.mark.parametrize("source", ["(1 + 2", "1 + * 2", "true =="])
def test_invalid_parser_input_returns_none(source: str, capsys) -> None:
    scanner = Scanner(source)
    scanner.scan_tokens()

    parser = Parser(scanner.tokens)
    statements = parser.parse()

    out = capsys.readouterr()
    assert parser.had_error is True
    assert statements == []
    assert "Error" in out.err


@pytest.mark.parametrize("source", ["@", '"unterminated'])
def test_invalid_scanner_input_raises(source: str) -> None:
    with pytest.raises(LoxScanError):
        Scanner(source).scan_tokens()

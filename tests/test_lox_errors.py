from lox import Lox


def test_run_success_prints_ast(capsys) -> None:
    lox = Lox()

    lox.run("1 + 2 * 3")

    out = capsys.readouterr()
    assert lox.had_error is False
    assert out.err == ""
    assert out.out.strip() == "7"


def test_run_scanner_error_sets_had_error(capsys) -> None:
    lox = Lox()

    lox.run("1 + @")

    out = capsys.readouterr()
    assert lox.had_error is True
    assert "Error" in out.err
    assert "Unrecognized token" in out.err


def test_run_parser_error_sets_had_error(capsys) -> None:
    lox = Lox()

    lox.run("(1 + 2")

    out = capsys.readouterr()
    assert lox.had_error is True
    assert "Error" in out.err
    assert "Expect ')' after expression." in out.err

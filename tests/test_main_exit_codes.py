import subprocess
import sys


def test_file_mode_exits_65_on_error(tmp_path) -> None:
    bad = tmp_path / "bad.lox"
    bad.write_text("1 + @", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "main.py", str(bad)],
        capture_output=True,
        text=True,
        cwd="/home/djean/projects/pylox",
    )

    assert result.returncode == 65
    assert "Error" in result.stderr

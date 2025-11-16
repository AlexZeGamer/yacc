import sys
from io import StringIO
from pathlib import Path

import pytest

from yacc.utils.errors import CompilationError


def run_main_with_args(args, capsys):
    from yacc.__main__ import main

    old_argv = sys.argv
    try:
        sys.argv = [old_argv[0], *args]
        main()
    finally:
        sys.argv = old_argv
    return capsys.readouterr().out


def test_parse_args_exclusive_inputs_error(capsys):
    from yacc.__main__ import parse_args

    old_argv = sys.argv
    try:
        # both positional and --string -> error
        sys.argv = [old_argv[0], "file.c", "--string", "1"]
        with pytest.raises(SystemExit):
            parse_args()
    finally:
        sys.argv = old_argv


def test_cli_main_stdout_string(capsys):
    program = "int main() { debug 1; }"
    out = run_main_with_args(["--string", program, "--stdout"], capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 1\ndbg\npush 0\nret\n"


def test_cli_main_stdout_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", StringIO("int main() { debug !0; }"))
    out = run_main_with_args(["--stdin", "--stdout"], capsys)
    assert out == ".start\nprep main\ncall 0\nhalt\n.main\npush 1\ndbg\npush 0\nret\n"


def test_cli_main_writes_file(tmp_path: Path):
    from yacc.__main__ import main

    input_text = "int main() { debug -2; }\n"
    input_file = tmp_path / "in.c"
    output_file = tmp_path / "out.asm"
    input_file.write_text(input_text, encoding="utf-8")

    old_argv = sys.argv
    try:
        sys.argv = [old_argv[0], str(input_file), "-o", str(output_file)]
        main()
    finally:
        sys.argv = old_argv

    content = output_file.read_text(encoding="utf-8")
    assert content == ".start\nprep main\ncall 0\nhalt\n.main\npush -2\ndbg\npush 0\nret\n"


def test_cli_invalid_program_raises_compilation_error(capsys):
    program = "int main() { break; }"
    with pytest.raises(CompilationError):
        run_main_with_args(["--string", program, "--stdout"], capsys)


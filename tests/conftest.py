import sys
from pathlib import Path


# Ensure the project src/ directory is importable in tests
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


import builtins  # noqa: E402
import io  # noqa: E402
import typing as _t  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def make_source():
    from yacc.source import Source

    def _make(text: str, name: str = "<test>"):
        return Source.from_string(text, name=name)

    return _make


def read_stdout(capsys) -> str:
    captured = capsys.readouterr()
    return captured.out


__all__: _t.Final[tuple[str, ...]] = (
    "make_source",
    "read_stdout",
)


from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Callable, Optional
from unittest.mock import patch

from tacxir import Parser, TacxIR, TacxIRError, tokenize


@dataclass
class RunResult:
    ok: bool
    output: str
    error: str = ""


def load_source(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _format_exception(exc: BaseException) -> str:
    if isinstance(exc, TacxIRError):
        return exc.format()
    return f"{type(exc).__name__}: {exc}"


def run_source(source: str, input_provider: Optional[Callable[[], str]] = None) -> RunResult:
    stdout = StringIO()
    try:
        tokens, src = tokenize(source)
        parser = Parser(tokens, src)
        program = parser.parse_program()
        interpreter = TacxIR(source=src)
        with redirect_stdout(stdout):
            if input_provider is None:
                interpreter.execute(program)
            else:
                with patch("builtins.input", side_effect=input_provider):
                    interpreter.execute(program)
        return RunResult(ok=True, output=stdout.getvalue())
    except BaseException as exc:  # noqa: BLE001 - deliberate GUI error boundary
        return RunResult(ok=False, output=stdout.getvalue(), error=_format_exception(exc))

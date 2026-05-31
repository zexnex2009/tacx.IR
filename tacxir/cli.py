import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .ast_nodes import ast_to_debug_lines, tokens_to_lines
from .errors import TacxIRError, TacxIRRuntimeError
from .interpreter import BreakException, ContinueException, ReturnException, TacxIR
from .parser import Parser
from .tokens import tokenize


def configure_stdio():
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tacxIR.py",
        description="Tacx.IR interpreter and debug tools",
    )
    parser.add_argument("file", nargs="?", help="Tacx.IR source file (use - for stdin)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dump-tokens", action="store_true", help="print the token stream and exit")
    mode.add_argument("--dump-ast", action="store_true", help="print the parsed AST and exit")
    return parser


def load_source(filename: str) -> str:
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found.")


def _wrap_error(exc: BaseException, interp: TacxIR) -> BaseException:
    if isinstance(exc, TacxIRError):
        return exc
    if isinstance(exc, (TypeError, ValueError, IndexError, ZeroDivisionError, NameError, RuntimeError)):
        line, col, source_line = interp._last_error_node_info()
        return TacxIRRuntimeError(str(exc), line=line, col=col, source_line=source_line)
    return exc


def run_source(source: str, *, dump_tokens: bool = False, dump_ast: bool = False, file_path: Optional[Path] = None):
    tokens, src = tokenize(source)
    if dump_tokens:
        return tokens_to_lines(tokens)
    parser = Parser(tokens, src)
    program = parser.parse_program()
    if dump_ast:
        lines: List[str] = []
        for stmt in program:
            lines.extend(ast_to_debug_lines(stmt))
        return lines
    interpreter = TacxIR(source=src)
    if file_path:
        interpreter.current_file = file_path.resolve()
    try:
        interpreter.execute(program)
    except (ReturnException, BreakException, ContinueException):
        raise
    except (TypeError, ValueError, IndexError, ZeroDivisionError, NameError, RuntimeError) as exc:
        raise _wrap_error(exc, interpreter) from exc
    return []


def main(argv: Optional[List[str]] = None) -> int:
    configure_stdio()
    parser = build_cli_parser()
    args = parser.parse_args(argv)

    source = None
    file_path = None

    if args.file == "-" or (args.file is None and not sys.stdin.isatty()):
        try:
            source = sys.stdin.read()
        except BrokenPipeError:
            return 0
        if not source.strip():
            print("Tacx.IR error: empty input from stdin", file=sys.stderr)
            return 1
    elif args.file:
        try:
            source = load_source(args.file)
            file_path = Path(args.file).resolve()
        except FileNotFoundError as e:
            print(f"Tacx.IR error: {e}", file=sys.stderr)
            return 1
    else:
        parser.print_help()
        return 1

    try:
        output_lines = run_source(source, dump_tokens=args.dump_tokens, dump_ast=args.dump_ast, file_path=file_path)
        for line in output_lines:
            print(line)
        return 0
    except BrokenPipeError:
        return 0
    except TacxIRError as e:
        print(f"Tacx.IR error: {e.format()}", file=sys.stderr)
        return 1
    except SyntaxError as e:
        print(f"Tacx.IR error: {e}", file=sys.stderr)
        return 1
    except (ReturnException, BreakException, ContinueException) as e:
        print(f"Tacx.IR error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Internal error: {e}", file=sys.stderr)
        return 1

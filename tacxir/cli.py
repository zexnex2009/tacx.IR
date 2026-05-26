import argparse
import sys
from typing import List, Optional

from .ast_nodes import ast_to_debug_lines, tokens_to_lines
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
    parser.add_argument("file", nargs="?", help="Tacx.IR source file")
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


def run_source(source: str, *, dump_tokens: bool = False, dump_ast: bool = False):
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
    interpreter = TacxIR()
    interpreter.execute(program)
    return []


def main(argv: Optional[List[str]] = None) -> int:
    configure_stdio()
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    if not args.file:
        parser.print_help()
        return 1

    try:
        source = load_source(args.file)
        output_lines = run_source(source, dump_tokens=args.dump_tokens, dump_ast=args.dump_ast)
        for line in output_lines:
            print(line)
        return 0
    except BrokenPipeError:
        return 0
    except (SyntaxError, RuntimeError, NameError, TypeError, ZeroDivisionError, IndexError, ValueError) as e:
        print(f"Tacx.IR error: {e}")
        return 1
    except (ReturnException, BreakException, ContinueException) as e:
        print(f"Tacx.IR error: {e}")
        return 1
    except Exception as e:
        print(f"Internal error: {e}")
        return 1


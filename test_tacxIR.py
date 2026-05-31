import io
from pathlib import Path
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from tacxIR import Parser, TacxIR, main, tokenize


def parse_program(source: str):
    tokens, src = tokenize(source)
    parser = Parser(tokens, src)
    return parser.parse_program()


def run_program(source: str, inputs=None) -> str:
    program = parse_program(source)
    interpreter = TacxIR()
    output = io.StringIO()
    with redirect_stdout(output):
        if inputs is None:
            interpreter.execute(program)
        else:
            with patch('builtins.input', side_effect=inputs):
                interpreter.execute(program)
    return output.getvalue()


def execute_program(source: str) -> TacxIR:
    interpreter = TacxIR()
    interpreter.execute(parse_program(source))
    return interpreter


def run_cli(args):
    output = io.StringIO()
    with redirect_stdout(output):
        code = main(args)
    return code, output.getvalue()


class TacxIRTests(unittest.TestCase):
    def test_naile_tokenizes_as_single_keyword(self):
        tokens, _ = tokenize("Jodi Sotyo { Bolo 1; } Naile { Bolo 2; }")
        self.assertIn("NAILE", [token.type for token in tokens])

    def test_function_locals_do_not_leak_to_global_scope(self):
        source = """
Dhori build() {
    Rakho $tmp = 10;
    dao $tmp;
}
Bolo build();
Bolo build();
"""
        output = run_program(source)
        self.assertEqual(output, "10\n10\n")

        interpreter = execute_program("""
Dhori build() {
    Rakho $tmp = 10;
    dao $tmp;
}
""")
        self.assertNotIn("$tmp", interpreter.globals)

    def test_modulo_operator(self):
        output = run_program('Bolo 5 % 2;')
        self.assertEqual(output, "1\n")


    def test_unary_minus_rejects_boolean(self):
        with self.assertRaisesRegex(TypeError, "Unary '-' requires number"):
            execute_program('Bolo -Sotyo;')

    def test_arithmetic_operators_reject_booleans(self):
        for expr in (
            'Bolo Sotyo + 1;',
            'Bolo 1 - Mithya;',
            'Bolo Sotyo * 3;',
            'Bolo 4 / Mithya;',
            'Bolo Sotyo % 2;',
        ):
            with self.assertRaisesRegex(TypeError, "requires numbers"):
                execute_program(expr)

    def test_cholao_rejects_fractional_count(self):
        with self.assertRaisesRegex(TypeError, "Cholao count must be a non-negative integer"):
            execute_program("""
Cholao 2.5 bar {
    Bolo 1;
}
""")

    def test_cholao_rejects_negative_count(self):
        with self.assertRaisesRegex(ValueError, "Cholao count must be non-negative"):
            execute_program("""
Cholao -1 bar {
    Bolo 1;
}
""")

    def test_index_assignment_updates_array(self):
        output = run_program("""
Rakho $nums = [1, 2, 3];
Rakho $nums[1] = 99;
Bolo $nums[1];
""")
        self.assertEqual(output, "99\n")

    def test_nested_index_assignment_updates_inner_array(self):
        output = run_program("""
Rakho $matrix = [[1, 2], [3, 4]];
Rakho $matrix[1][0] = 8;
Bolo $matrix[1][0];
""")
        self.assertEqual(output, "8\n")

    def test_fractional_index_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "Index must be an integer"):
            execute_program("""
Rakho $nums = [1, 2, 3];
Bolo $nums[1.5];
""")

    def test_fractional_index_assignment_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "Index must be an integer"):
            execute_program("""
Rakho $nums = [1, 2, 3];
Rakho $nums[1.5] = 7;
""")

    def test_array_assignment_out_of_bounds_fails(self):
        with self.assertRaisesRegex(IndexError, "out of bounds"):
            execute_program("""
Rakho $nums = [1, 2, 3];
Rakho $nums[5] = 7;
""")

    def test_block_scoped_locals_do_not_leak_from_conditionals(self):
        with self.assertRaisesRegex(NameError, r"Variable '\$tmp' is not defined"):
            execute_program("""
jodi sotyo {
    rakho $tmp = 10;
}
bolo $tmp;
""")

    def test_logical_and_short_circuits(self):
        output = run_program('Bolo Mithya Ebong (1 / 0);')
        self.assertEqual(output, "False\n")

    def test_logical_or_short_circuits(self):
        output = run_program('Bolo Sotyo Othoba (1 / 0);')
        self.assertEqual(output, "True\n")

    def test_return_outside_function_is_runtime_error(self):
        tokens, src = tokenize("dao 1;")
        parser = Parser(tokens, src)
        program = parser.parse_program()
        interpreter = TacxIR()
        with self.assertRaisesRegex(RuntimeError, "Dao can only be used inside a function"):
            interpreter.execute(program)

    def test_break_outside_loop_is_runtime_error(self):
        tokens, src = tokenize("Thamo;")
        parser = Parser(tokens, src)
        program = parser.parse_program()
        interpreter = TacxIR()
        with self.assertRaisesRegex(RuntimeError, "Thamo can only be used inside a loop"):
            interpreter.execute(program)

    def test_lomba_builtin_works_for_array_and_string(self):
        output = run_program("""
Rakho $nums = [1, 2, 3];
Bolo Lomba($nums);
Bolo Lomba("abc");
""")
        self.assertEqual(output, "3\n3\n")

    def test_dhukao_and_berkoro_builtins_mutate_arrays(self):
        output = run_program("""
Rakho $nums = [1, 2];
Bolo Dhukao($nums, 5);
Bolo Lomba($nums);
Bolo BerKoro($nums);
Bolo Lomba($nums);
""")
        self.assertEqual(output, "3\n3\n5\n2\n")

    def test_dhoron_builtin_reports_runtime_types(self):
        output = run_program("""
Bolo Dhoron(10);
Bolo Dhoron("hi");
Bolo Dhoron([1, 2]);
Bolo Dhoron(Sotyo);
""")
        self.assertEqual(output, "shonkha\nlekha\ntalika\nsotyo-mithya\n")


    def test_mixed_type_ordered_comparison_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "requires comparable values"):
            execute_program('Bolo 10 < "2";')

    def test_number_comparison_does_not_treat_bool_as_number(self):
        with self.assertRaisesRegex(TypeError, "requires comparable values"):
            execute_program('Bolo Sotyo < 2;')

    def test_boolean_ordered_comparison_is_rejected(self):
        with self.assertRaisesRegex(TypeError, "requires comparable values"):
            execute_program('Bolo Sotyo < Mithya;')

    def test_string_ordered_comparison_still_works(self):
        output = run_program('Bolo "a" < "b";')
        self.assertEqual(output, "True\n")

    def test_builtin_arity_errors_are_clear(self):
        with self.assertRaisesRegex(TypeError, "Builtin 'Lomba' expects 1 arguments, got 0"):
            execute_program("Bolo Lomba();")

    def test_escaped_strings_are_decoded(self):
        output = run_program('Bolo "line1\\nline2"; Bolo "quote: \\"x\\""; Bolo "tab\\tend";')
        self.assertEqual(output, 'line1\nline2\nquote: "x"\ntab\tend\n')

    def test_invalid_string_escape_is_rejected(self):
        with self.assertRaisesRegex(SyntaxError, "Unsupported escape sequence"):
            parse_program('Bolo "\\q";')

    def test_strength_sample_smoke(self):
        sample = Path(__file__).with_name('v2strengthtext.tacx').read_text(encoding='utf-8')
        output = run_program(sample, inputs=['Alice', '20'])
        self.assertIn("All Tests Completed Successfully!", output)
        self.assertIn("Tacx.IR is STRONG!", output)

    def test_cli_dump_tokens(self):
        path = Path(__file__).with_name('_cli_sample.tacx')
        try:
            path.write_text('Bolo 1 + 2;', encoding='utf-8')
            code, output = run_cli(['--dump-tokens', str(path)])
        finally:
            if path.exists():
                path.unlink()
        self.assertEqual(code, 0)
        self.assertIn("BOLO", output)
        self.assertIn("PLUS", output)

    def test_cli_dump_ast(self):
        path = Path(__file__).with_name('_cli_sample.tacx')
        try:
            path.write_text('Bolo 1 + 2;', encoding='utf-8')
            code, output = run_cli(['--dump-ast', str(path)])
        finally:
            if path.exists():
                path.unlink()
        self.assertEqual(code, 0)
        self.assertIn("BoloStmt", output)
        self.assertIn("BinOp(+)", output)


# ---- New feature tests ----

class TacxIRSourceAwareTests(unittest.TestCase):
    def test_ast_node_stores_position(self):
        from tacxir.ast_nodes import NumberNode
        n = NumberNode(42, line=3, col=5)
        self.assertEqual(n.line, 3)
        self.assertEqual(n.col, 5)

    def test_runtime_error_format_includes_line_and_col(self):
        from tacxir.errors import TacxIRRuntimeError
        err = TacxIRRuntimeError("test error", line=2, col=8, source_line="bolo 1 + 2;")
        formatted = err.format()
        self.assertIn("line 2", formatted)
        self.assertIn("col 8", formatted)
        self.assertIn("test error", formatted)
        self.assertIn("1 + 2", formatted)

    def test_runtime_error_format_without_position(self):
        from tacxir.errors import TacxIRRuntimeError
        err = TacxIRRuntimeError("plain error")
        formatted = err.format()
        self.assertEqual(formatted, "plain error")

    def test_cli_wraps_runtime_errors(self):
        from tacxir.cli import run_source
        with self.assertRaisesRegex(RuntimeError, "Division by zero"):
            run_source("bolo 1 / 0;")


class TacxIRCanonicalVarTests(unittest.TestCase):
    def test_dollar_and_bare_are_identical(self):
        output = run_program("""
rakho $x = 42;
bolo x;
""")
        self.assertEqual(output, "42\n")

    def test_assign_to_bare_reads_via_dollar(self):
        output = run_program("""
rakho $x = 99;
bolo x;
""")
        self.assertEqual(output, "99\n")

    def test_function_scope_canonical(self):
        output = run_program("""
dhori foo(a) {
    bolo $a;
}
foo(10);
""")
        self.assertEqual(output, "10\n")


class TacxIRSlicingTests(unittest.TestCase):
    def test_slice_stop_only(self):
        output = run_program("""
rakho $arr = [0, 1, 2, 3, 4];
bolo $arr[:3];
""")
        self.assertEqual(output, "[0, 1, 2]\n")

    def test_slice_start_only(self):
        output = run_program("""
rakho $arr = [0, 1, 2, 3, 4];
bolo $arr[2:];
""")
        self.assertEqual(output, "[2, 3, 4]\n")

    def test_slice_start_stop(self):
        output = run_program("""
rakho $arr = [0, 1, 2, 3, 4];
bolo $arr[1:4];
""")
        self.assertEqual(output, "[1, 2, 3]\n")

    def test_slice_full(self):
        output = run_program("""
rakho $arr = [0, 1, 2, 3, 4];
bolo $arr[:];
""")
        self.assertEqual(output, "[0, 1, 2, 3, 4]\n")

    def test_slice_string(self):
        output = run_program("""
bolo "hello"[:3];
""")
        self.assertEqual(output, "hel\n")

    def test_slice_string_with_start(self):
        output = run_program("""
bolo "hello"[2:];
""")
        self.assertEqual(output, "llo\n")

    def test_slice_non_array_or_string_raises(self):
        with self.assertRaisesRegex(TypeError, "Can only slice arrays or strings"):
            execute_program("bolo 42[:2];")


class TacxIRStdinTests(unittest.TestCase):
    def test_stdin_dash_flag(self):
        import sys
        from tacxir.cli import main
        test_input = 'bolo 1 + 2;'
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(test_input)
        try:
            code, output = None, None
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main(['-'])
            self.assertEqual(code, 0)
            self.assertEqual(buf.getvalue().strip(), '3')
        finally:
            sys.stdin = old_stdin

    def test_stdin_implicit_pipe(self):
        import sys
        from tacxir.cli import main
        test_input = 'bolo 42;'
        old_stdin = sys.stdin
        old_isatty = sys.stdin.isatty
        sys.stdin = io.StringIO(test_input)
        sys.stdin.isatty = lambda: False
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                code = main([])
            self.assertEqual(code, 0)
            self.assertEqual(buf.getvalue().strip(), '42')
        finally:
            sys.stdin.isatty = old_isatty
            sys.stdin = old_stdin


class TacxIRNewBuiltinsTests(unittest.TestCase):
    def test_mul_identity(self):
        output = run_program("bolo mul(5);")
        self.assertEqual(output, "5\n")

    def test_ghat_power(self):
        output = run_program("bolo ghat(2, 3);")
        self.assertEqual(output, "8\n")

    def test_boro_max(self):
        output = run_program("bolo boro(10, 20);")
        self.assertEqual(output, "20\n")

    def test_choto_min(self):
        output = run_program("bolo choto(10, 20);")
        self.assertEqual(output, "10\n")

    def test_bhag_split(self):
        output = run_program('bolo bhag("a,b,c", ",");')
        self.assertEqual(output, "['a', 'b', 'c']\n")

    def test_jora_join(self):
        output = run_program('bolo jora(["x", "y"], "-");')
        self.assertEqual(output, "x-y\n")

    def test_borhat_upper(self):
        output = run_program('bolo borhat("hello");')
        self.assertEqual(output, "HELLO\n")

    def test_chothat_lower(self):
        output = run_program('bolo chothat("HELLO");')
        self.assertEqual(output, "hello\n")

    def test_porofile_reads_file(self):
        from tempfile import NamedTemporaryFile
        import os
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write("hello world")
            f.flush()
            fname = f.name.replace("\\", "/")
        try:
            output = run_program(f'bolo porofile("{fname}");')
            self.assertEqual(output, "hello world\n")
        finally:
            os.unlink(fname)

    def test_lekhofile_writes_file(self):
        from tempfile import NamedTemporaryFile
        import os
        with NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            fname = f.name.replace("\\", "/")
        try:
            output = run_program(f'bolo lekhofile("{fname}", "test content");')
            self.assertEqual(output, "12\n")
            with open(fname, 'r', encoding='utf-8') as f:
                self.assertEqual(f.read(), "test content")
        finally:
            os.unlink(fname)

    def test_porofile_not_found(self):
        with self.assertRaisesRegex(FileNotFoundError, "File not found"):
            execute_program('bolo porofile("nonexistent.tacx");')

    def test_bhag_type_error(self):
        with self.assertRaisesRegex(TypeError, "bhag expects a string"):
            execute_program('bolo bhag(42, ",");')

    def test_jora_type_error(self):
        with self.assertRaisesRegex(TypeError, "jora expects an array"):
            execute_program('bolo jora("x", "-");')


class TacxIRSyntaxAliasTests(unittest.TestCase):
    def test_amdo_tokenizes(self):
        from tacxir.tokens import tokenize
        tokens, _ = tokenize('amdo "utils.tacx";')
        types = [t.type for t in tokens]
        self.assertIn("AMDO", types)

    def test_amdo_parses(self):
        from tacxir.ast_nodes import AmdoStmt
        tokens, src = tokenize('amdo "utils.tacx";')
        parser = __import__("tacxir.parser", fromlist=["Parser"]).Parser(tokens, src)
        program = parser.parse_program()
        self.assertEqual(len(program), 1)
        self.assertIsInstance(program[0], AmdoStmt)
        self.assertEqual(program[0].path, "utils.tacx")


class TacxIRImportTests(unittest.TestCase):
    def test_import_syntax_parses(self):
        from tempfile import TemporaryDirectory
        from tacxir.cli import run_source
        with TemporaryDirectory() as tmp:
            main_path = Path(tmp) / "main.tacx"
            utils_path = Path(tmp) / "utils.tacx"
            utils_path.write_text('dhori greet() { bolo "hi"; }', encoding="utf-8")
            main_path.write_text('amdo "utils.tacx"; greet();', encoding="utf-8")
            output = run_source(main_path.read_text(encoding="utf-8"), file_path=main_path)
            self.assertEqual(output, [])

    def test_import_executes_imported_code(self):
        from tempfile import TemporaryDirectory
        from tacxir.cli import run_source
        with TemporaryDirectory() as tmp:
            main_path = Path(tmp) / "main.tacx"
            utils_path = Path(tmp) / "utils.tacx"
            utils_path.write_text('dhori greet() { bolo "hi"; }', encoding="utf-8")
            main_path.write_text('amdo "utils.tacx"; greet();', encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                run_source(main_path.read_text(encoding="utf-8"), file_path=main_path)
            self.assertIn("hi", stdout.getvalue())

    def test_import_no_duplicate_execution(self):
        from tempfile import TemporaryDirectory
        from tacxir.cli import run_source
        with TemporaryDirectory() as tmp:
            main_path = Path(tmp) / "main.tacx"
            utils_path = Path(tmp) / "utils.tacx"
            utils_path.write_text('bolo "imported";', encoding="utf-8")
            main_path.write_text('amdo "utils.tacx"; amdo "utils.tacx";', encoding="utf-8")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                run_source(main_path.read_text(encoding="utf-8"), file_path=main_path)
            self.assertEqual(stdout.getvalue().count("imported"), 1)

    def test_import_circular_detection(self):
        from tempfile import TemporaryDirectory
        from tacxir.cli import run_source
        with TemporaryDirectory() as tmp:
            a_path = Path(tmp) / "a.tacx"
            b_path = Path(tmp) / "b.tacx"
            a_path.write_text('amdo "b.tacx";', encoding="utf-8")
            b_path.write_text('amdo "a.tacx";', encoding="utf-8")
            with self.assertRaises(RuntimeError):
                run_source(a_path.read_text(encoding="utf-8"), file_path=a_path)

    def test_import_missing_file(self):
        from tempfile import TemporaryDirectory
        from tacxir.cli import run_source
        with TemporaryDirectory() as tmp:
            main_path = Path(tmp) / "main.tacx"
            main_path.write_text('amdo "missing.tacx";', encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                run_source(main_path.read_text(encoding="utf-8"), file_path=main_path)


if __name__ == "__main__":
    unittest.main()

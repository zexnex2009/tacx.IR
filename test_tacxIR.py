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


if __name__ == "__main__":
    unittest.main()

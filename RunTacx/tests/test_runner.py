import unittest

from RunTacx.runner import run_source


class RunTacxRunnerTests(unittest.TestCase):
    def test_run_source_captures_output(self):
        result = run_source('bolo "hi";')
        self.assertTrue(result.ok)
        self.assertEqual(result.output, "hi\n")
        self.assertEqual(result.error, "")

    def test_run_source_handles_input(self):
        result = run_source(
            "poro $name; bolo $name;",
            input_provider=lambda: "Alice",
        )
        self.assertTrue(result.ok)
        self.assertEqual(result.output, "Alice\n")

    def test_run_source_reports_errors(self):
        result = run_source('bolo 1 / 0;')
        self.assertFalse(result.ok)
        self.assertIn("ZeroDivisionError", result.error)


if __name__ == "__main__":
    unittest.main()


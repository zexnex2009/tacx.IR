import shutil
import unittest
import uuid
from pathlib import Path

from RunTacx.project import discover_example_files, normalize_recent_files


class RunTacxProjectTests(unittest.TestCase):
    def test_discover_example_files_finds_hello_example(self):
        names = [path.name for path in discover_example_files()]
        self.assertIn("hello.tacx", names)

    def test_normalize_recent_files_deduplicates_and_limits(self):
        root = Path(__file__).resolve().parents[1] / f"_tmp_{uuid.uuid4().hex}"
        try:
            root.mkdir(parents=True, exist_ok=False)
            first = root / "a.tacx"
            second = root / "b.tacx"
            first.write_text("bolo 1;", encoding="utf-8")
            second.write_text("bolo 2;", encoding="utf-8")

            entries = [str(first), str(first), str(second)]
            result = normalize_recent_files(entries, limit=5)

            self.assertEqual(result, [str(first.resolve()), str(second.resolve())])
        finally:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

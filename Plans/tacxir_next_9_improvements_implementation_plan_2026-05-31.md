# Tacx.IR Next 9 Improvements Implementation Plan

Date: 2026-05-31

This plan is grounded in the current repository state. The current test baseline is green (`35/35`), so the next work should preserve that baseline while improving reliability, diagnostics, and language ergonomics.

The plan is ordered by expected impact and implementation risk.

---

## 1. Source-Aware Diagnostics and Runtime Tracebacks

### Goal
Give every parser/runtime failure a consistent line/column location and a short source excerpt, instead of only `TypeError: ...` or `RuntimeError: ...`.

### Files to change
- `tacxir/ast_nodes.py`
- `tacxir/parser.py`
- `tacxir/interpreter.py`
- `tacxir/cli.py`
- `RunTacx/runner.py`
- `test_tacxIR.py`

### Functions and logic to modify
- `Parser._error`
- `Parser.parse_*` methods that create AST nodes
- `TacxIR.eval_expr`
- `TacxIR.execute`
- `run_source`
- `main`
- `RunTacx.runner._format_exception`

### What to write
- Add optional position fields to AST nodes.
- Add a custom exception hierarchy in the runtime, for example:

```py
class TacxIRError(RuntimeError):
    pass

class TacxIRRuntimeError(TacxIRError):
    def __init__(self, message, *, line=None, col=None, source_line=""):
        super().__init__(message)
        self.line = line
        self.col = col
        self.source_line = source_line
```

- Capture token position when building AST nodes and preserve it through evaluation.
- Format runtime errors in a single reusable helper.

### How to do it
1. Extend `ASTNode` so every node can optionally store `line` and `col`.
2. In the parser, when consuming the token that introduced an expression or statement, pass that token's position into the created node.
3. In the interpreter, before evaluating a node, set `self.current_node = node` or use a small wrapper.
4. Wrap common runtime failures (`TypeError`, `ValueError`, `IndexError`, `ZeroDivisionError`, `NameError`, `RuntimeError`) into `TacxIRRuntimeError` only when they come from Tacx.IR execution, not from control-flow exceptions.
5. Update CLI and `RunTacx` to print the formatted message.

### Core snippet
```py
try:
    value = self.eval_expr(node)
except (TypeError, ValueError, IndexError, ZeroDivisionError, NameError) as exc:
    raise TacxIRRuntimeError(str(exc), line=node.line, col=node.col) from exc
```

### Possible errors and handling
- Do not catch `ReturnException`, `BreakException`, or `ContinueException` inside the runtime error wrapper.
- If a node has no position metadata, print a plain error message rather than failing the formatter.
- Ensure CLI still returns non-zero exit code on failure.

### Necessary notes / quotations
- Existing parser errors already do source location formatting:
  - `raise SyntaxError(f"{msg} at line {line}, col {col} ...")`
- Existing runtime code currently raises plain Python exceptions from deep inside evaluation:
  - `raise TypeError("Operator '+' requires numbers when not concatenating strings")`

---

## 2. Module Imports (`amdo`)

### Goal
Allow `.tacx` files to import other `.tacx` files, with circular-import detection and relative-path resolution.

### Files to change
- `tacxir/tokens.py`
- `tacxir/parser.py`
- `tacxir/interpreter.py`
- `tacxir/cli.py`
- `RunTacx/highlighter.py`
- `test_tacxIR.py`

### Functions and logic to modify
- `TOKEN_TYPES`
- `KEYWORD_TOKEN_TYPES`
- `Parser.parse_statement`
- `TacxIR.execute`
- `run_source`
- `load_source`

### What to write
- Add a new `AMDO` token.
- Add a new AST statement node, e.g. `AmdoStmt`.
- Add interpreter state to track:
  - the current file path
  - imported file cache
  - import stack for cycle detection

### How to do it
1. Update the lexer to recognize `amdo` case-insensitively as a keyword.
2. Extend the parser:

```py
elif tok.type == "AMDO":
    self.consume("AMDO")
    path_tok = self.consume("STRING")
    self.consume("SEMI")
    return AmdoStmt(self.decode_string_literal(path_tok))
```

3. Update the interpreter so `AmdoStmt` resolves the path relative to the current source file.
4. Parse the imported file with a fresh parser, but execute it in the same global interpreter state.
5. Prevent re-importing the same file multiple times.
6. Detect circular imports before executing the target.

### Core snippet
```py
resolved = (base_dir / import_path).resolve()
if resolved in self.import_stack:
    raise RuntimeError(f"Circular import detected: {resolved}")
if resolved not in self.imported_files:
    self.imported_files.add(resolved)
    self.execute(imported_program)
```

### Possible errors and handling
- `FileNotFoundError` for missing imports.
- `SyntaxError` from imported file parsing should include the imported file path.
- Circular import should fail fast with a clear message.
- Guard against path traversal by resolving relative to the current file.

### Necessary notes / quotations
- The roadmap already defines the syntax as `amdo "utils.tacx";`.
- `tacxIR.py` should remain a compatibility shim; the import machinery belongs in the package runtime, not the root script.

---

## 3. Canonical Variable Identity

### Goal
Make `$x` and `x` map to one canonical binding model instead of being able to diverge silently.

### Files to change
- `tacxir/interpreter.py`
- `test_tacxIR.py`

### Functions and logic to modify
- `_get_var`
- `_set_var`
- `_declare_var`
- `eval_expr` for `VarNode`
- function-call local scope setup in `eval_expr(CallNode)`

### What to write
- Add one canonicalization helper:

```py
def _canon_name(name: str) -> str:
    return name[1:] if name.startswith("$") else name
```

- Apply canonicalization whenever a variable is read or written.

### How to do it
1. Normalize the name before every scope lookup or assignment.
2. Normalize function parameters when storing them in the local scope.
3. Keep the user-facing error message, but refer to the canonicalized name when needed.

### Core snippet
```py
name = self._canon_name(name)
for scope in reversed(self.scopes):
    if name in scope:
        return scope[name]
```

### Possible errors and handling
- This is a behavioral change. Existing programs that intentionally depended on `$x` and `x` being distinct will change behavior.
- Update docs/changelog so the new behavior is explicit.

### Necessary notes / quotations
- Current code path to fix:
  - `if node.name.startswith("$"): return self._get_var(node.name)`
  - `self.scopes[-1][name] = value`

---

## 4. Array and String Slicing

### Goal
Support slice syntax like `$arr[1:4]`, `$arr[:4]`, `$arr[1:]`, and string slicing with the same semantics.

### Files to change
- `tacxir/tokens.py`
- `tacxir/ast_nodes.py`
- `tacxir/parser.py`
- `tacxir/interpreter.py`
- `test_tacxIR.py`

### Functions and logic to modify
- `TOKEN_TYPES`
- `Parser.parse_postfix`
- `Parser.parse_assignment_target` only if nested slicing on targets is intentionally supported
- `ast_to_debug_lines`
- `TacxIR.eval_expr`

### What to write
- Add `COLON` to the token list.
- Add `SliceNode(obj, start, stop)`.
- Teach postfix parsing to distinguish index versus slice.

### How to do it
1. Tokenize `:`.
2. In `parse_postfix`, when parsing `[...]`, detect whether a colon exists inside the brackets.
3. Build either `IndexNode` or `SliceNode`.
4. In the interpreter, evaluate `SliceNode` against `list` or `str`.
5. Reuse existing integer coercion for bounds.

### Core snippet
```py
if tok and tok.type == "COLON":
    self.consume("COLON")
    stop = None if self.peek().type == "RBRACKET" else self.parse_expression()
    self.consume("RBRACKET")
    expr = SliceNode(expr, start, stop)
```

### Possible errors and handling
- If a slice target is not a list or string, raise `TypeError("Can only slice arrays or strings")`.
- If bounds are non-integers, raise the same integer-coercion error used for indexing.
- If `]` is missing, let the parser fail through the existing `_error` path.

### Necessary notes / quotations
- Current code already handles indexing in `parse_postfix()` with:
  - `expr = IndexNode(expr, index)`
- Reuse that branch instead of creating a second parser flow.

---

## 5. Expanded Builtin Standard Library

### Goal
Add useful builtins for string operations, math helpers, and local file I/O while keeping arity/type errors predictable.

### Files to change
- `tacxir/interpreter.py`
- `RunTacx/highlighter.py`
- `README.md`
- `Guide/02_Math_and_Text.md`
- `test_tacxIR.py`

### Functions and logic to modify
- `TacxIR.__init__`
- `_builtin_lomba`
- `_builtin_dhukao`
- `_builtin_berkoro`
- `_builtin_dhoron`
- new builtin helpers

### What to write
- New builtins can be grouped like this:
  - math: `mul`, `ghat`, `boro`, `choto`
  - strings: `bhag`, `jora`, `borhat`, `chothat`
  - files: `porofile`, `lekhofile`
- Register aliases in `self.builtins`.

### How to do it
1. Add one helper per builtin operation.
2. Use `_expect_arity` for argument count checks.
3. Validate input types before calling Python helpers.
4. For file I/O, restrict paths to local filesystem use only.
5. Update syntax highlighting to include the new names.

### Core snippet
```py
self.builtins["mul"] = self._builtin_sqrt
self.builtins["bhag"] = self._builtin_split
self.builtins["jora"] = self._builtin_join
```

### Possible errors and handling
- `TypeError` for wrong types or wrong arity.
- `ValueError` for invalid numeric conversions or unsupported math input.
- `PermissionError` or a custom runtime error if file access escapes the allowed root.
- `FileNotFoundError` for missing readable files.

### Necessary notes / quotations
- Current builtin registry is already centralized:
  - `self.builtins: Dict[str, Callable[[List[Any]], Any]] = { ... }`
- The GUI highlighter must be kept in sync:
  - `BUILTINS = {"lomba", "dhukao", "dhuk", "berkoro", "berkr", "dhoron", "dhron"}`

---

## 6. Unified CLI and RunTacx Error Rendering

### Goal
Make command-line and desktop error output consistent and readable.

### Files to change
- `tacxir/cli.py`
- `RunTacx/runner.py`
- `RunTacx/app.py`
- new `tacxir/errors.py`

### Functions and logic to modify
- `main`
- `run_source`
- `_format_exception`
- `_handle_run_result`

### What to write
- Centralize exception formatting in a reusable helper.
- Preserve control-flow exceptions separately from normal runtime errors.

### How to do it
1. Add `TacxIRError`/`TacxIRRuntimeError` helpers.
2. Make the CLI catch them explicitly.
3. Return or display the formatted traceback string.
4. Keep `BrokenPipeError` and `KeyboardInterrupt` behavior normal.

### Core snippet
```py
except TacxIRError as exc:
    print(exc.format())
    return 1
```

### Possible errors and handling
- Do not over-catch `Exception` before control-flow cleanup.
- GUI should still append output and show a message box for the formatted error string.

### Necessary notes / quotations
- Current runner code is too shallow:
  - `return f"{type(exc).__name__}: {exc}"`
- Current CLI error handler collapses many exceptions into one line:
  - `print(f"Tacx.IR error: {e}")`

---

## 7. Syntax Alias Cleanup and Highlighter Sync

### Goal
Put keyword and builtin aliases behind one source of truth so the lexer and GUI highlighter cannot drift apart.

### Files to change
- `tacxir/tokens.py`
- `RunTacx/highlighter.py`
- `README.md`

### Functions and logic to modify
- `keyword_pattern`
- `TOKEN_TYPES`
- `KEYWORD_TOKEN_TYPES`
- `TacxSyntaxHighlighter._build_rules`

### What to write
- Replace scattered alias strings with a canonical alias map.
- Reuse that map for both tokenization and syntax highlighting.

### How to do it
1. Define a single alias registry for keywords and builtins.
2. Generate regex patterns from that registry.
3. Update the highlighter sets from the same canonical list.

### Core snippet
```py
ALIASES = {
    "JOTOKHON": ("jtkhn", "jotokhon"),
    "OTHOBA": ("ba", "othoba"),
}
```

### Possible errors and handling
- Avoid alias collisions where one alias becomes a substring of another valid token.
- Keep the canonical lowercase spellings unchanged.

### Necessary notes / quotations
- The lexer already lowercases keyword lexemes:
  - `if kind in KEYWORD_TOKEN_TYPES: value = value.lower()`
- The syntax highlighter currently hard-codes the builtin names in a set, so it must be updated whenever the lexer names change.

---

## 8. stdin / Piped Input Mode

### Goal
Allow `tacxIR.py` to read source from stdin so the language can be used in shell pipelines.

### Files to change
- `tacxir/cli.py`
- optionally `tacxIR.py`

### Functions and logic to modify
- `build_cli_parser`
- `main`
- `run_source`

### What to write
- Support `-` as a file placeholder.
- Support implicit stdin when no file is supplied and stdin is not a TTY.

### How to do it
1. Add an input mode branch in `main`.
2. If input is `-`, read `sys.stdin.read()`.
3. If no file argument is provided but stdin has data, also read from stdin.
4. Keep the existing help output when neither file nor piped input is available.

### Core snippet
```py
if args.file == "-" or (args.file is None and not sys.stdin.isatty()):
    source = sys.stdin.read()
```

### Possible errors and handling
- Empty stdin should still return a useful help or empty-input error.
- `BrokenPipeError` should remain a clean exit path.
- Do not break `python tacxIR.py script.tacx`.

### Necessary notes / quotations
- Current behavior is file-only:
  - `if not args.file: parser.print_help(); return 1`

---

## 9. Regression Test Harness Expansion

### Goal
Add tests for the new behavior while keeping the current suite hermetic and portable.

### Files to change
- `test_tacxIR.py`
- `RunTacx/tests/test_runner.py`
- `RunTacx/tests/test_project.py`

### Functions and logic to modify
- `run_program`
- `execute_program`
- `run_cli`
- new temp-file helpers

### What to write
- Table-driven tests for:
  - imports
  - tracebacks
  - slices
  - builtin alias parity
  - canonical variable lookup
  - stdin execution
  - file I/O builtin failures

### How to do it
1. Add temp-file fixtures using `TemporaryDirectory` or `Path` under the test directory.
2. Reuse `redirect_stdout` and `patch("builtins.input", ...)`.
3. Assert both success output and exact error class/message for failure cases.

### Core snippet
```py
with TemporaryDirectory() as tmp:
    main_path = Path(tmp) / "main.tacx"
    main_path.write_text('amdo "utils.tacx"; bolo add(1, 2);', encoding="utf-8")
```

### Possible errors and handling
- Windows cleanup issues: always delete temp files/directories in `finally`.
- Avoid shared global interpreter state between tests.
- Keep tests deterministic by avoiding real user input and real external files.

### Necessary notes / quotations
- The existing suite already uses the right pattern:
  - `redirect_stdout(output)`
  - `patch('builtins.input', side_effect=inputs)`
  - temporary sample files for CLI tests

---

## Recommended Implementation Order

1. Source-aware diagnostics
2. Unified CLI / RunTacx error rendering
3. Canonical variable identity
4. Array and string slicing
5. Syntax alias cleanup and highlighter sync
6. stdin / piped input mode
7. Expanded builtins
8. Module imports
9. Regression test harness expansion

This order minimizes rework: diagnostics and error plumbing should land before new language features because they make the next failures easier to understand.

---

## Acceptance Criteria

- Existing tests remain green.
- New tests cover each improvement path.
- CLI and GUI show consistent error formatting.
- New syntax is reflected in both lexer and highlighter.
- New language features do not leak state or break existing scripts.


# 🗺️ Tacx.IR Language Evolution Roadmap

This roadmap outlines the top 5 high-impact architectural and feature improvements proposed for **Tacx.IR**. Each improvement addresses existing limitations in language usability, diagnostics, scoping, or modularity, and is accompanied by a concrete syntax design and modular implementation plan.

---

## 📌 Executive Summary of Proposed Improvements

| Priority | Improvement Option | Primary Impact | Affected Modules |
| :---: | :--- | :--- | :--- |
| **1** | [Module System & File Imports (`Amdo`)](#1-module-system--file-imports-amdo) | Modularity & Code Reuse | Lexer, Parser, Interpreter, CLI |
| **2** | [Position-Aware AST & Runtime Tracebacks](#2-position-aware-ast--detailed-runtime-tracebacks) | Developer Experience & Diagnostics | Lexer, Parser, AST, Interpreter |
| **3** | [True Block Scoping & Variable Shadowing](#3-true-block-scoping--variable-shadowing) | Language Safety & Consistency | Interpreter |
| **4** | [Expanded Builtin Standard Library](#4-expanded-builtin-standard-library-string-math-file-io) | Math, Strings, and File Operations | Interpreter |
| **5** | [Array Slicing Support](#5-array-slicing-support) | Rich Data Manipulation | Parser, AST, Interpreter |

---

## 1. Module System & File Imports (`Amdo`)

### 💡 Description & Motivation
Currently, Tacx.IR programs are monolithic; all code must exist in a single `.tacx` file. As applications grow, this becomes unsustainable. Introducing the `Amdo` (transliterated Bengali for "import/bring") keyword will allow developers to load external `.tacx` files, promoting modular program architecture, code reuse, and standard library components.

### 🎭 Proposed Syntax
```tacx
// utils.tacx
Dhori add(x, y) {
    Ferot x + y;
}

// main.tacx
Amdo "utils.tacx";

Rakho $res = add(10, 20);
Bolo $res; // Prints 30
```

### 🛠️ Implementation Plan
1. **[`tokens.py`](tacxir/tokens.py)**:
   * Define `AMDO` token regex: `("AMDO", keyword_pattern("Amdo"))`.
2. **[`ast_nodes.py`](tacxir/ast_nodes.py)**:
   * Create `AmdoStmt(StmtNode)` with `path: str`. Add debug rendering in `ast_to_debug_lines`.
3. **[`parser.py`](tacxir/parser.py)**:
   * Parse the import statement:
     ```python
     elif tok.type == "AMDO":
         self.consume("AMDO")
         path_tok = self.consume("STRING")
         self.consume("SEMI")
         return AmdoStmt(self.decode_string_literal(path_tok))
     ```
4. **[`interpreter.py`](tacxir/interpreter.py)**:
   * Add tracking for already-imported modules to prevent circular imports (e.g. `self.imported_files = set()`).
   * When evaluating `AmdoStmt`:
     1. Resolve file path relative to the current file.
     2. Read and parse the target file.
     3. Recursively execute its statements inside the interpreter's global scope, keeping function/variable names defined in the current environment context.
5. **[`test_tacxIR.py`](test_tacxIR.py)**:
   * Write test suites generating temporary `.tacx` files using python `pathlib` and asserting correct cross-file execution and namespace visibility.

---

## 2. Position-Aware AST & Detailed Runtime Tracebacks

### 💡 Description & Motivation
While parsing errors report line and column coordinates, runtime errors (such as `ZeroDivisionError`, `TypeError` inside addition, or `IndexError` on arrays) output generic Python exceptions without source file context. This makes debugging large `.tacx` scripts difficult.
Making the AST position-aware allows the interpreter to output professional runtime stack tracebacks with the exact line and column numbers where the exception occurred.

### 🎭 Proposed Syntax/Diagnostics
```text
Tacx.IR Runtime Error: Division by zero
  at line 14, col 23 (operator '/')
  in statement Bolo 100 / $var;
```

### 🛠️ Implementation Plan
1. **[`ast_nodes.py`](tacxir/ast_nodes.py)**:
   * Modify the base `ASTNode` to accept optional `line` and `col` fields:
     ```python
     class ASTNode:
         def __init__(self, line: int = None, col: int = None):
             self.line = line
             self.col = col
     ```
   * Update all expression and statement nodes to pass position metadata to their `__init__` constructor.
2. **[`parser.py`](tacxir/parser.py)**:
   * Capture the position of primary operator tokens (e.g. `LPAREN`, `PLUS`, keywords) using the lexer `pos_to_linecol` utility.
   * Attach line and column coordinates to every created AST Node.
3. **[`interpreter.py`](tacxir/interpreter.py)**:
   * Create a helper context manager or execution wrapper to track the current executing node: `self.current_node: ASTNode`.
   * Catch runtime exceptions (e.g. `TypeError`, `ZeroDivisionError`, `IndexError`) and wrap them in a custom `TacxIRRuntimeError` that embeds `self.current_node` position details.
4. **[`cli.py`](tacxir/cli.py)**:
   * Format `TacxIRRuntimeError` into a human-readable traceback block containing source line context.

---

## 3. True Block Scoping & Variable Shadowing

### 💡 Description & Motivation
In Tacx.IR's current architecture, only functions (`Dhori`) establish new variable lookup scopes. If a developer uses a temporary variable inside a `Jodi` conditional block or `Jotokhon` loop, that variable leaks out and contaminates the parent function or global scope.
Introducing block scopes inside `{}` braces prevents namespace contamination and supports variable shadowing.

### 🎭 Proposed Syntax
```tacx
Rakho $x = 10;

Jodi Sotyo {
    // Declares a block-local variable that shadows the outer $x
    Rakho $x = 99; 
    Bolo $x; // Prints 99
}

Bolo $x; // Prints 10 (retains original value!)
```

### 🛠️ Implementation Plan
1. **[`interpreter.py`](tacxir/interpreter.py)**:
   * Currently, scope frames are in a stack list `self.scopes: List[Dict[str, Any]]`.
   * Add helper methods to handle block entry/exit:
     * `enter_block_scope()`: Pushes a new empty scope dictionary onto the stack.
     * `exit_block_scope()`: Pops the top scope dictionary off the stack.
   * When evaluating `JodiStmt`, `CholaoStmt`, or `JotokhonStmt`:
     * Execute their statement body lists inside block scope boundaries:
       ```python
       self.enter_block_scope()
       try:
           self.execute(stmt.body)
       finally:
           self.exit_block_scope()
       ```
2. **Variable Resolving Rule adjustments**:
   * Change `_set_var` to only assign to an existing variable if it is declared in the current or parent scopes. If it is a fresh identifier defined with `Rakho` inside the block, keep it local to the active block scope level.
3. **[`test_tacxIR.py`](test_tacxIR.py)**:
   * Write test suites containing variables redefined inside nested loops/conditionals, and assert that outer values remain untouched after block exit.

---

## 4. Expanded Builtin Standard Library (String, Math, File I/O)

### 💡 Description & Motivation
Currently, Tacx.IR only includes 4 builtins (`Lomba`, `Dhukao`, `BerKoro`, `Dhoron`). Developers cannot perform basic floating-point math, string splitting, or read/write file streams. Adding standard library builtins dramatically improves what can be built.

### 🎭 Proposed Syntax
```tacx
// Math utilities
Rakho $root = Borgomul(16); // 4.0
Rakho $power = Ghat(2, 3); // 8.0

// String manipulation
Rakho $words = Bhaago("hello world", " "); // ["hello", "world"]

// File I/O
Rakho $content = PoroFile("data.txt");
Bolo $content;
```

### 🛠️ Implementation Plan
1. **[`interpreter.py`](tacxir/interpreter.py)**:
   * Register new built-in hooks inside `self.builtins` in `__init__`:
     * **Math**:
       * `"Borgomul"`: `math.sqrt` logic.
       * `"Ghat"`: `math.pow` logic.
       * `"Boro"`: `max()` logic.
       * `"Choto"`: `min()` logic.
     * **Strings**:
       * `"Bhaago"`: splits a string by delimiter, returns an array.
       * `"JoraDao"`: joins an array of strings by delimiter, returns a string.
       * `"BoroLekha"`: returns upper-case string.
       * `"ChhotoLekha"`: returns lower-case string.
     * **File Access**:
       * `"PoroFile"`: reads file contents to a string.
       * `"LekhoFile"`: writes string contents to a file.
2. **Safety & Security constraints**:
   * Ensure that File access builtins resolve paths only inside the allowed user directories to prevent sandbox escapes.
3. **[`test_tacxIR.py`](test_tacxIR.py)**:
   * Write comprehensive tests asserting correct floating-point math, string manipulation lists, and secure read/write cycles.

---

## 5. Array Slicing Support

### 💡 Description & Motivation
Currently, arrays only support basic element indexing (`$arr[i]`). To extract subsets or slice arrays, developers must write manual loops. Supporting slicing syntax `$arr[start:end]` brings Tacx.IR closer to Python's capabilities.

### 🎭 Proposed Syntax
```tacx
Rakho $nums = [10, 20, 30, 40, 50];
Rakho $sub = $nums[1:4];
Bolo $sub; // Prints [20, 30, 40]
```

### 🛠️ Implementation Plan
1. **[`tokens.py`](tacxir/tokens.py)**:
   * Add a colon token representation to lex strings: `("COLON", r":")`.
2. **[`ast_nodes.py`](tacxir/ast_nodes.py)**:
   * Introduce a new AST node `SliceNode(ASTNode)` representing `obj`, `start_expr`, and `end_expr`. Update `ast_to_debug_lines`.
3. **[`parser.py`](tacxir/parser.py)**:
   * Update the primary index parsing sequence inside `parse_postfix` to detect the `COLON` delimiter inside bracket expressions:
     ```python
     if tok.type == "LBRACKET":
         self.consume("LBRACKET")
         first = self.parse_expression()
         if self.peek() and self.peek().type == "COLON":
             self.consume("COLON")
             second = self.parse_expression()
             self.consume("RBRACKET")
             expr = SliceNode(expr, first, second)
         else:
             self.consume("RBRACKET")
             expr = IndexNode(expr, first)
     ```
4. **[`interpreter.py`](tacxir/interpreter.py)**:
   * Add a handler in `eval_expr` for `SliceNode`:
     * Evaluate `obj` (must be list or string).
     * Evaluate `start_expr` and `end_expr` (must be integers).
     * Return standard Python slice results: `container[start:end]`.
5. **[`test_tacxIR.py`](test_tacxIR.py)**:
   * Write tests testing string slices, array slices, boundary clipping, and type boundary validation.

# 🗺️ Tacx.IR Language Evolution Roadmap

This roadmap outlines the top 6 high-impact architectural and feature improvements proposed for **Tacx.IR**. Each improvement addresses existing limitations in language usability, diagnostics, scoping, or modularity, and is accompanied by a concrete syntax design and modular implementation plan.

---

## 📌 Executive Summary of Proposed Improvements

| Priority | Improvement Option | Primary Impact | Affected Modules |
| :---: | --- | --- | --- |
| **1** | [Module System & File Imports (](#1-module-system--file-imports-amdo)`[amdo](#1-module-system--file-imports-amdo)`[)](#1-module-system--file-imports-amdo) | Modularity & Code Reuse | Lexer, Parser, Interpreter, CLI |
| **2** | [Position-Aware AST & Runtime Tracebacks](#2-position-aware-ast--detailed-runtime-tracebacks) | Developer Experience & Diagnostics | Lexer, Parser, AST, Interpreter |
| **3** | [True Block Scoping & Variable Shadowing](#3-true-block-scoping--variable-shadowing) | Language Safety & Consistency | Interpreter |
| **4** | [Expanded Builtin Standard Library](#4-expanded-builtin-standard-library-string-math-file-io) | Math, Strings, and File Operations | Interpreter |
| **5** | [Array Slicing Support](#5-array-slicing-support) | Rich Data Manipulation | Parser, AST, Interpreter |
| **6** | [Syntax Simplification & Keyword Shorthands](#6-syntax-simplification--keyword-shorthands) | Code Conciseness & Readability | Lexer, Parser, Interpreter |

---

## 1. Module System & File Imports (`amdo`)

### 💡 Description & Motivation

Currently, Tacx.IR programs are monolithic; all code must exist in a single `.tacx` file. As applications grow, this becomes unsustainable. Introducing the `amdo` (transliterated Bengali for "import/bring") keyword will allow developers to load external `.tacx` files, promoting modular program architecture, code reuse, and standard library components.

### 🎭 Proposed Syntax

```tacx
// utils.tacx
dhori add(x, y) {
    dao x + y;
}

// main.tacx
amdo "utils.tacx";

rakho $res = add(10, 20);
bolo $res; // Prints 30
```

### 🛠️ Implementation Plan

1. **`[tokens.py](tacxir/tokens.py)`**:
   - Define `AMDO` token regex: `("AMDO", keyword_pattern("amdo"))`.
2. **`[ast_nodes.py](tacxir/ast_nodes.py)`**:
   - Create `AmdoStmt(StmtNode)` with `path: str`. Add debug rendering in `ast_to_debug_lines`.
3. **`[parser.py](tacxir/parser.py)`**:
   - Parse the import statement:

     ```python
     elif tok.type == "AMDO":  
         self.consume("AMDO")  
         path_tok = self.consume("STRING")  
         self.consume("SEMI")  
         return AmdoStmt(self.decode_string_literal(path_tok))  
     ```
4. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Add tracking for already-imported modules to prevent circular imports (e.g. `self.imported_files = set()`).
   - When evaluating `AmdoStmt`:
     1. Resolve file path relative to the current file.
     2. Read and parse the target file.
     3. Recursively execute its statements inside the interpreter's global scope, keeping function/variable names defined in the current environment context.
5. **`[test_tacxIR.py](test_tacxIR.py)`**:
   - Write test suites generating temporary `.tacx` files using python `pathlib` and asserting correct cross-file execution and namespace visibility.

---

## 2. Position-Aware AST & Detailed Runtime Tracebacks

### 💡 Description & Motivation

While parsing errors report line and column coordinates, runtime errors (such as `ZeroDivisionError`, `TypeError` inside addition, or `IndexError` on arrays) output generic Python exceptions without source file context. This makes debugging large `.tacx` scripts difficult.  
Making the AST position-aware allows the interpreter to output professional runtime stack tracebacks with the exact line and column numbers where the exception occurred.

### 🎭 Proposed Syntax/Diagnostics

```text
Tacx.IR Runtime Error: Division by zero
  at line 14, col 23 (operator '/')
  in statement bolo 100 / $var;
```

### 🛠️ Implementation Plan

1. **`[ast_nodes.py](tacxir/ast_nodes.py)`**:
   - Modify the base `ASTNode` to accept optional `line` and `col` fields:

     ```python
     class ASTNode:  
         def __init__(self, line: int = None, col: int = None):  
             self.line = line  
             self.col = col  
     ```
   - Update all expression and statement nodes to pass position metadata to their `__init__` constructor.
2. **`[parser.py](tacxir/parser.py)`**:
   - Capture the position of primary operator tokens (e.g. `LPAREN`, `PLUS`, keywords) using the lexer `pos_to_linecol` utility.
   - Attach line and column coordinates to every created AST Node.
3. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Create a helper context manager or execution wrapper to track the current executing node: `self.current_node: ASTNode`.
   - Catch runtime exceptions (e.g. `TypeError`, `ZeroDivisionError`, `IndexError`) and wrap them in a custom `TacxIRRuntimeError` that embeds `self.current_node` position details.
4. **`[cli.py](tacxir/cli.py)`**:
   - Format `TacxIRRuntimeError` into a human-readable traceback block containing source line context.

---

## 3. True Block Scoping & Variable Shadowing

### 💡 Description & Motivation

In Tacx.IR's current architecture, only functions (`dhori`) establish new variable lookup scopes. If a developer uses a temporary variable inside a `jodi` conditional block or `jtkhn` loop, that variable leaks out and contaminates the parent function or global scope.  
Introducing block scopes inside `{}` braces prevents namespace contamination and supports variable shadowing.

### 🎭 Proposed Syntax

```tacx
rakho $x = 10;

jodi sotyo {
    // Declares a block-local variable that shadows the outer $x
    rakho $x = 99; 
    bolo $x; // Prints 99
}

bolo $x; // Prints 10 (retains original value!)
```

### 🛠️ Implementation Plan

1. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Currently, scope frames are in a stack list `self.scopes: List[Dict[str, Any]]`.
   - Add helper methods to handle block entry/exit:
     - `enter_block_scope()`: Pushes a new empty scope dictionary onto the stack.
     - `exit_block_scope()`: Pops the top scope dictionary off the stack.
   - When evaluating `JodiStmt`, `CholaoStmt`, or `JotokhonStmt`:
     - Execute their statement body lists inside block scope boundaries:

       ```python
       self.enter_block_scope()  
       try:  
           self.execute(stmt.body)  
       finally:  
           self.exit_block_scope()  
       ```
2. **Variable Resolving Rule adjustments**:
   - Change `_set_var` to only assign to an existing variable if it is declared in the current or parent scopes. If it is a fresh identifier defined with `rakho` inside the block, keep it local to the active block scope level.
3. **`[test_tacxIR.py](test_tacxIR.py)`**:
   - Write test suites containing variables redefined inside nested loops/conditionals, and assert that outer values remain untouched after block exit.

---

## 4. Expanded Builtin Standard Library (String, Math, File I/O)

### 💡 Description & Motivation

Currently, Tacx.IR only includes 4 builtins (`lomba`, `dhukao`, `berkoro`, `dhoron`). Developers cannot perform basic floating-point math, string splitting, or read/write file streams. Adding standard library builtins dramatically improves what can be built.

### 🎭 Proposed Syntax

```tacx
// Math utilities
rakho $root = borgomul(16); // 4.0
rakho $power = ghat(2, 3); // 8.0

// String manipulation
rakho $words = bhaago("hello world", " "); // ["hello", "world"]

// File I/O
rakho $content = porofile("data.txt");
bolo $content;
```

### 🛠️ Implementation Plan

1. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Register new built-in hooks inside `self.builtins` in `__init__`:
     - **Math**:
       - `"borgomul"`: `math.sqrt` logic.
       - `"ghat"`: `math.pow` logic.
       - `"boro"`: `max()` logic.
       - `"choto"`: `min()` logic.
     - **Strings**:
       - `"bhaago"`: splits a string by delimiter, returns an array.
       - `"joradao"`: joins an array of strings by delimiter, returns a string.
       - `"borolekha"`: returns upper-case string.
       - `"chhotolekha"`: returns lower-case string.
     - **File Access**:
       - `"porofile"`: reads file contents to a string.
       - `"lekhofile"`: writes string contents to a file.
2. **Safety & Security constraints**:
   - Ensure that File access builtins resolve paths only inside the allowed user directories to prevent sandbox escapes.
3. **`[test_tacxIR.py](test_tacxIR.py)`**:
   - Write comprehensive tests asserting correct floating-point math, string manipulation lists, and secure read/write cycles.

---

## 5. Array Slicing Support

### 💡 Description & Motivation

Currently, arrays only support basic element indexing (`$arr[i]`). To extract subsets or slice arrays, developers must write manual loops. Supporting slicing syntax `$arr[start:end]` brings Tacx.IR closer to Python's capabilities.

### 🎭 Proposed Syntax

```tacx
rakho $nums = [10, 20, 30, 40, 50];
rakho $sub = $nums[1:4];
bolo $sub; // Prints [20, 30, 40]
```

### 🛠️ Implementation Plan

1. **`[tokens.py](tacxir/tokens.py)`**:
   - Add a colon token representation to lex strings: `("COLON", r":")`.
2. **`[ast_nodes.py](tacxir/ast_nodes.py)`**:
   - Introduce a new AST node `SliceNode(ASTNode)` representing `obj`, `start_expr`, and `end_expr`. Update `ast_to_debug_lines`.
3. **`[parser.py](tacxir/parser.py)`**:
   - Update the primary index parsing sequence inside `parse_postfix` to detect the `COLON` delimiter inside bracket expressions:

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
4. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Add a handler in `eval_expr` for `SliceNode`:
     - Evaluate `obj` (must be list or string).
     - Evaluate `start_expr` and `end_expr` (must be integers).
     - Return standard Python slice results: `container[start:end]`.
5. **`[test_tacxIR.py](test_tacxIR.py)`**:
   - Write tests testing string slices, array slices, boundary clipping, and type boundary validation.

---

## 6. Syntax Simplification & Keyword Shorthands

### 💡 Description & Motivation

While Tacx.IR's Banglish keywords are deeply expressive, some common keywords and built-in functions are verbose to type repetitively in long scripts (e.g., `jotokhon` is 8 characters long; `othoba` is 6). Furthermore, some previous simplification ideas introduced semantic conflicts (e.g., using `boro` for uppercase strings heavily conflicts with the "greater than" meaning).

To simplify syntax naturally and authentically without breaking existing programs, we propose a **conversational shorthand aliasing system**. This introduces refined, linguistically accurate alternatives for high-frequency operations. 

**Note: Keywords are accepted case-insensitively; lowercase remains the canonical style.**

### 🎭 Comparison of Verbose vs. Simplified Shorthand

| Verbose Syntax / Built-in | Proposed Shorthand | Meaning / Description | Chars Saved |
| --- | --- | --- | :---: |
| **`jotokhon`** | **`jtkhn`** | Loop: while loop keyword. | **37%** (8 $\rightarrow$ 5) |
| **`othoba`** | **`ba`** | Operator: Logical OR. *"Ba"* is natural Banglish for "or". | **66%** (6 $\rightarrow$ 2) |
| **`ebong`** | **`ar`** | Operator: Logical AND. *"Ar"* is natural Banglish for "and". | **60%** (5 $\rightarrow$ 2) |
| **`cholao`** | **`kor`** | Loop: count-based loop keyword (*"kor"* = do). | **50%** (6 $\rightarrow$ 3) |
| **`chalano`** | **`chal`** | Loop: "continue" instruction. *"chal"* means "go/move". | **42%** (7 $\rightarrow$ 4) |
| **`thamo`** | **`tham`** | Loop: "break" instruction. | **20%** (5 $\rightarrow$ 4) |
| **`ferot`** | **`dao`** | Keyword: returns a value from a function (*"dao"* = give). | **40%** (5 $\rightarrow$ 3) |
| **`dhori`** | **`dhori`** | Keyword: function definition (unchanged). | **0%** (5 $\rightarrow$ 5) |
| **`berkoro(...)`** | **`berkr(...)`** | Built-in: pops/removes last item of an array. | **28%** (7 $\rightarrow$ 5) |
| **`dhukao(...)`** | **`dhuk(...)`** | Built-in: appends a value into an array. | **33%** (6 $\rightarrow$ 4) |
| **`bhaago(...)`** | **`bhag(...)`** | Built-in: splits a string by delimiter (*"bhag"* = divide/split). | **33%** (6 $\rightarrow$ 4) |
| **`joradao(...)`** | **`jora(...)`** | Built-in: joins an array of strings. | **43%** (7 $\rightarrow$ 4) |
| **`dhoron(...)`** | **`dhron(...)`** | Built-in: returns the type of a value. | **16%** (6 $\rightarrow$ 5) |
| **`borgomul(...)`** | **`mul(...)`** | Built-in: mathematical square root. | **62%** (8 $\rightarrow$ 3) |
| **`borolekha(...)`** | **`borhat(...)`** | Built-in: uppercase string converter ("borhat" = boro hater). | **33%** (9 $\rightarrow$ 6) |
| **`chhotolekha(...)`** | **`chothat(...)`** | Built-in: lowercase string converter ("chothat" = chhoto hater). | **36%** (11 $\rightarrow$ 7) |

#### Shortened Code Example

```tacx
// BEFORE (Verbose)
dhori factorial(n) {
    jodi n <= 1 {
        ferot 1;
    } naile {
        ferot n * factorial(n - 1);
    }
}

rakho $arr = [1, 2];
jotokhon lomba($arr) > 0 ebong sotyo {
    rakho $val = berkoro($arr);
    chalano;
}

// AFTER (Shorthand)
dhori factorial(n) {
    jodi n <= 1 {
        dao 1;
    } naile {
        dao n * factorial(n - 1);
    }
}

rakho $arr = [1, 2];
jtkhn lomba($arr) > 0 ar sotyo {
    rakho $val = berkr($arr);
    chal;
}
```

### 🛠️ Backward-Compatible Implementation Plan

To keep lowercase as the canonical style while remaining backward compatible with mixed-case source text, we will deploy a refined **Lexical and Runtime Aliasing Strategy**:

1. **`[tokens.py](tacxir/tokens.py)`**:
   - Keep `keyword_pattern` anchored to whole words and normalize keyword lexemes to lowercase.
   - Map shorthand keywords to the *same* existing token types in the Lexer.

     ```python
     # In TOKEN_TYPES mapping list (using lowercase patterns):  
     ("JOTOKHON", keyword_pattern("jtkhn|jotokhon")),  
     ("OTHOBA", keyword_pattern("ba|othoba")),  
     ("EBONG", keyword_pattern("ar|ebong")),  
     ("CHALANO", keyword_pattern("chal|chalano")),  
     ("CHOLAO", keyword_pattern("kor|cholao")),
     ("THAMO", keyword_pattern("tham|thamo")),
     ("FEROT", keyword_pattern("dao|ferot")),
     ("DHORI", keyword_pattern("dhori")),
     ```
2. **`[interpreter.py](tacxir/interpreter.py)`**:
   - Register the new shorthands as aliases pointing to the same Python callable routines, ensuring all names are registered in lowercase:

     ```python
     # In self.builtins map registration:  
     self.builtins["berkoro"] = self._builtin_berkoro  
     self.builtins["berkr"] = self._builtin_berkoro  # Alias  
     
     self.builtins["dhukao"] = self._builtin_dhukao  
     self.builtins["dhuk"] = self._builtin_dhukao  # Alias  
     
     self.builtins["borgomul"] = self._builtin_borgomul  
     self.builtins["mul"] = self._builtin_borgomul  # Alias  

     self.builtins["dhoron"] = self._builtin_dhoron
     self.builtins["dhron"] = self._builtin_dhoron  # Alias
     ```
3. **`[test_tacxIR.py](test_tacxIR.py)`**:
   - Write unit tests validating that lowercase shorthands evaluate correctly and that mixed-case forms remain backward compatible.

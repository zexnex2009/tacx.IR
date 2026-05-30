# 🇧🇩 Tacx.IR — A Banglish-Inspired Programming Language

[![Language](https://img.shields.io/badge/Language-Banglish--Inspired-red.svg)]()
[![Backend](https://img.shields.io/badge/Backend-Python%203-blue.svg)]()
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)]()

> **Tacx.IR** is a modern, lightweight, dynamic programming language featuring syntax inspired by **Banglish** (conversational Bengali transliterated to Latin script). It compiles to a clean Abstract Syntax Tree (AST) and is evaluated by an optimized Python-based recursive-descent interpreter.
>
> Designed to combine the charm of everyday language with rigorous compiler design, Tacx.IR offers full support for variables, complex arrays, structured control flow, functions, and powerful built-in functions.
>
> **Note: Tacx.IR keywords are matched case-insensitively; lowercase remains the canonical style.**

---

## 📖 Table of Contents

1. [Key Features](#-key-features)
2. [Language Syntax Cheat Sheet](#-language-syntax-cheat-sheet)
3. [Core Types & Literals](#-core-types--literals)
4. [Built-In Functions](#-built-in-functions)
5. [Syntax & Code Showcase](#-syntax--code-showcase)
6. [Architecture & Project Layout](#-architecture--project-layout)
7. [Quick Start & CLI Usage](#-quick-start--cli-usage)
8. [Testing & Verification](#-testing--verification)

---

## ✨ Key Features

* **Modular Architecture**: Clean separation between Lexer/Tokenization, Recursive-Descent Parser, and runtime Interpreter.
* **Banglish Grammar**: Logical operations, variables, conditionals, and loops map directly to common Banglish phrases.
* **Robust Type System**: Includes dynamic types for strings, floats, integers, boolean literals, and multi-dimensional arrays.
* **Array Mutation**: Supports indexing, multi-dimensional list reading/writing, appending, and popping.
* **Block-Local Scopes**: Conditional and loop bodies get their own local scope, so temporary values do not leak outward.
* **Short-Circuit Logic**: Short-circuits conditional evaluations for performance and safety.
* **Command Line Diagnostics**: Provides detailed debug options to dump token streams or print a fully indented AST tree.

---

## 🗺️ Language Syntax Cheat Sheet

| Banglish Keyword | Standard Equivalent | Category | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`rakho`** | `let` / `=` | Assignment | Declares or reassigns a variable or index | `rakho $x = 10;` |
| **`bolo`** | `print` | Output | Evaluates and prints to standard output | `bolo "hello world";` |
| **`poro`** | `input` | Input | Reads input and infers type (number/string) | `poro $age;` |
| **`jodi`** | `if` | Conditional | Starts a conditional block | `jodi $x > 5 { ... }` |
| **`naile`** | `else` | Conditional | Defines the fallback branch of a conditional | `naile { ... }` |
| **`kor`** ... `bar`| `repeat` | Loop | Executes a block a fixed number of times | `kor 5 bar { ... }` |
| **`jtkhn`** | `while` | Loop | Executes a block while condition remains truthy| `jtkhn $i < 5 { ... }` |
| **`dhori`** | `function` | Declaration | Declares a new callable function | `dhori add(a, b) { ... }`|
| **`dao`** | `return` | Control Flow | Returns a value from a function | `dao a + b;` |
| **`tham`** | `break` | Control Flow | Immediately exits the innermost loop | `tham;` |
| **`chal`** | `continue` | Control Flow | Jumps to the next iteration of the loop | `chal;` |
| **`sotyo`** | `True` | Literal | Boolean True literal | `rakho $ok = sotyo;` |
| **`mithya`** | `False` | Literal | Boolean False literal | `rakho $fail = mithya;` |
| **`ar`** | `and` | Operator | Short-circuiting logical AND | `$x ar $y` |
| **`ba`** | `or` | Operator | Short-circuiting logical OR | `$x ba $y` |
| **`na`** | `not` | Operator | Unary logical negation (NOT) | `na $x` |

---

## 🧪 Core Types & Literals

Tacx.IR has a simple but strong dynamic type model supporting several distinct categories:

### 1. Numbers (`shonkha`)
Represents both integers and floating-point values.
* *Example:* `42`, `-3.14159`, `0`

### 2. Strings (`lekha`)
Double-quoted Unicode text. Fully supports standard escapes:
* `\n` (newline), `\t` (horizontal tab), `\r` (carriage return), `\"` (double quote), and `\\` (backslash).
* *Example:* `"hello\nworld"`

### 3. Booleans (`sotyo-mithya`)
Represented by the keyword literals:
* `sotyo` (logical true)
* `mithya` (logical false)

### 4. Arrays (`talika`)
Mutable, dynamic lists containing any mixture of data types, including nested lists.
* *Literal notation:* `[1, "two", sotyo, [100, 200]]`
* *Indexing (0-based):* `$arr[0]`
* *Nested Indexing:* `$arr[3][1]` (evaluates to `200`)
* *Assignment:* `rakho $arr[1] = "new_val";`

### 5. Falsy/Truthy Rules
The following values are evaluated as **falsy** by conditional structures:
* `mithya` (Boolean False)
* `0` and `0.0` (Numeric zero)
* `""` (Empty string)
* `[]` (Empty array)

All other values are evaluated as **truthy**.

---

## 🛠️ Built-In Functions

Tacx.IR includes utility functions for essential computations:

### 1. `lomba(x)`
Returns the length of a string or array.
* **Arguments**: Exactly 1.
* **Errors**: `TypeError` if `x` is not a string or array.
* **Example**:
  ```tacx
  rakho $myList = [1, 2, 3];
  bolo lomba($myList); // Prints 3
  bolo lomba("banglish"); // Prints 8
  ```

### 2. `dhuk(arr, value)`
Appends `value` to the end of the mutable array `arr`. Returns the **new length** of the array.
* **Arguments**: Exactly 2 (an array and the value to append).
* **Errors**: `TypeError` if the first argument is not an array.
* **Example**:
  ```tacx
  rakho $arr = [10];
  rakho $newLen = dhuk($arr, 20); // $arr is now [10, 20]
  bolo $newLen; // Prints 2
  ```

### 3. `berkr(arr)`
Removes and returns the last element of the array `arr` (standard pop operation).
* **Arguments**: Exactly 1.
* **Errors**: `TypeError` if not an array, `RuntimeError` if the array is empty.
* **Example**:
  ```tacx
  rakho $arr = [1, 2, 99];
  rakho $lastVal = berkr($arr); // $arr is now [1, 2]
  bolo $lastVal; // Prints 99
  ```

### 4. `dhron(x)`
Reports the runtime type classification of `x` as a readable string.
* **Arguments**: Exactly 1.
* **Return Values**:
  * `khali` (if internal Python `None`; user-facing `khali` literal is not yet available in syntax)
  * `sotyo-mithya` (if Boolean)
  * `shonkha` (if integer or float)
  * `lekha` (if string)
  * `talika` (if array)
  * Otherwise, returns the internal Python class name.
* **Example**:
  ```tacx
  bolo dhron(10.5);       // Prints "shonkha"
  bolo dhron("test");     // Prints "lekha"
  bolo dhron(mithya);     // Prints "sotyo-mithya"
  ```

---

## 🎨 Syntax & Code Showcase

### 🔁 Fibonacci Sequence (Recursion & Conditions)
```tacx
// Recursive Fibonacci function
dhori fibonacci(n) {
    jodi n == 0 { dao 0; }
    jodi n == 1 { dao 1; }
    dao fibonacci(n - 1) + fibonacci(n - 2);
}

bolo "fibonacci of 10 is:";
bolo fibonacci(10); // Prints 55
```

### 🏎️ Complex Array & Loop Summation
```tacx
dhori sumArray(arr, len) {
    rakho $total = 0;
    rakho $i = 0;
    jtkhn $i < len {
        rakho $total = $total + arr[$i];
        rakho $i = $i + 1;
    }
    dao $total;
}

rakho $nums = [10, 20, 30, 40];
bolo sumArray($nums, lomba($nums)); // Prints 100
```

### 🔁 While Loops with Break/Continue
```tacx
rakho $k = 0;
jtkhn $k < 10 {
    rakho $k = $k + 1;
    
    // Skip 3 using continue
    jodi $k == 3 {
        chal;
    }
    
    // Stop loop at 7 using break
    jodi $k == 7 {
        tham;
    }
    
    bolo $k;
}
// Outputs: 1, 2, 4, 5, 6
```

---

## 🏗️ Architecture & Project Layout

The compiler & interpreter modules are placed modularly in the [`tacxir`](tacxir/) package. Below is the file mapping:

* **[`tacxIR.py`](tacxIR.py)**: The main compatibility entry point. Preserves retro shell usages and maps to the underlying package APIs.
* **[`tacxir/__init__.py`](tacxir/__init__.py)**: Package initializer exposing public APIs (`Parser`, `TacxIR`, `tokenize`, `main`).
* **[`tacxir/tokens.py`](tacxir/tokens.py)**: High-performance regular expression tokenizer (Lexer). Keyword tokens are matched case-insensitively and normalized to lowercase values.
* **[`tacxir/ast_nodes.py`](tacxir/ast_nodes.py)**: Concrete classes representing every language expression and statement node, along with structured stringifiers for debugging.
* **[`tacxir/parser.py`](tacxir/parser.py)**: Recursive-descent parser mapping token lists into clean Abstract Syntax Trees, handling operator precedence and escape sequence decode boundaries.
* **[`tacxir/interpreter.py`](tacxir/interpreter.py)**: The runtime manager. Handles lexical scoping, function frames, loop break/continue exception bubbling, and builtin calculations.
* **[`tacxir/cli.py`](tacxir/cli.py)**: The main command-line interface suite. Operates streaming setups and routes runtime or dump tasks.
* **[`test_tacxIR.py`](test_tacxIR.py)**: A comprehensive regression test suite featuring extensive coverage for tokens, edge cases, scope, structures, and execution.
* **[`v2strengthtext.tacx`](v2strengthtext.tacx)**: A comprehensive strength test script illustrating all language capabilities in a single script.

---

## 🚀 Quick Start & CLI Usage

### Run a Tacx.IR script
To execute a source script directly:
```powershell
python tacxIR.py .\v2strengthtext.tacx
```

### Lexer Diagnostics (Token Dump)
To inspect the output of the lexical scanner without running the interpreter:
```powershell
python tacxIR.py --dump-tokens .\v2strengthtext.tacx
```
*Outputs token types in uppercase, with keyword values normalized to lowercase:*
```text
BOLO         bolo
NUMBER       1
PLUS         +
NUMBER       2
SEMI         ;
```

### Parser Diagnostics (AST Dump)
To review the compiled Abstract Syntax Tree structural tree:
```powershell
python tacxIR.py --dump-ast .\v2strengthtext.tacx
```
*Outputs tree in format:*
```text
BoloStmt
  BinOp(+)
    Number(1)
    Number(2)
```

---

## 🛡️ Testing & Verification

The project includes full unit testing via Python's built-in `unittest` module.

To run the suite with maximum verbosity:
```powershell
python -m unittest -v test_tacxIR.py
```

Before contributing, always make sure the entire suite runs with no failures or errors.

# 🇧🇩 Tacx.IR — A Banglish-Inspired Programming Language

[![Language](https://img.shields.io/badge/Language-Banglish--Inspired-red.svg)]()
[![Backend](https://img.shields.io/badge/Backend-Python%203-blue.svg)]()
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)]()

> **Tacx.IR** is a modern, lightweight, dynamic programming language featuring syntax inspired by **Banglish** (conversational Bengali transliterated to Latin script). It compiles to a clean Abstract Syntax Tree (AST) and is evaluated by an optimized Python-based recursive-descent interpreter.
>
> Designed to combine the charm of everyday language with rigorous compiler design, Tacx.IR offers full support for variables, complex arrays, structured control flow, functions, and powerful built-in functions.

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
* **Short-Circuit Logic**: Short-circuits conditional evaluations for performance and safety.
* **Command Line Diagnostics**: Provides detailed debug options to dump token streams or print a fully indented AST tree.

---

## 🗺️ Language Syntax Cheat Sheet

| Banglish Keyword | Standard Equivalent | Category | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| **`Rakho`** | `let` / `=` | Assignment | Declares or reassigns a variable or index | `Rakho $x = 10;` |
| **`Bolo`** | `print` | Output | Evaluates and prints to standard output | `Bolo "Hello World";` |
| **`Poro`** | `input` | Input | Reads input and infers type (number/string) | `Poro $age;` |
| **`Jodi`** | `if` | Conditional | Starts a conditional block | `Jodi $x > 5 { ... }` |
| **`Naile`** | `else` | Conditional | Defines the fallback branch of a conditional | `Naile { ... }` |
| **`Cholao` ... `bar`**| `repeat` | Loop | Executes a block a fixed number of times | `Cholao 5 bar { ... }` |
| **`Jotokhon`** | `while` | Loop | Executes a block while condition remains truthy| `Jotokhon $i < 5 { ... }` |
| **`Dhori`** | `function` | Declaration | Declares a new callable function | `Dhori add(a, b) { ... }`|
| **`Ferot`** | `return` | Control Flow | Returns a value from a function | `Ferot a + b;` |
| **`Thamo`** | `break` | Control Flow | Immediately exits the innermost loop | `Thamo;` |
| **`Chalano`** | `continue` | Control Flow | Jumps to the next iteration of the loop | `Chalano;` |
| **`Sotyo`** | `True` | Literal | Boolean True literal | `Rakho $ok = Sotyo;` |
| **`Mithya`** | `False` | Literal | Boolean False literal | `Rakho $fail = Mithya;` |
| **`Ebong`** | `and` | Operator | Short-circuiting logical AND | `$x Ebong $y` |
| **`Othoba`** | `or` | Operator | Short-circuiting logical OR | `$x Othoba $y` |
| **`Na`** | `not` | Operator | Unary logical negation (NOT) | `Na $x` |

---

## 🧪 Core Types & Literals

Tacx.IR has a simple but strong dynamic type model supporting several distinct categories:

### 1. Numbers (`shonkha`)
Represents both integers and floating-point values.
* *Example:* `42`, `-3.14159`, `0`

### 2. Strings (`lekha`)
Double-quoted Unicode text. Fully supports standard escapes:
* `\n` (newline), `\t` (horizontal tab), `\r` (carriage return), `\"` (double quote), and `\\` (backslash).
* *Example:* `"Hello\nWorld"`

### 3. Booleans (`sotyo-mithya`)
Represented by the keyword literals:
* `Sotyo` (logical true)
* `Mithya` (logical false)

### 4. Arrays (`talika`)
Mutable, dynamic lists containing any mixture of data types, including nested lists.
* *Literal notation:* `[1, "two", Sotyo, [100, 200]]`
* *Indexing (0-based):* `$arr[0]`
* *Nested Indexing:* `$arr[3][1]` (evaluates to `200`)
* *Assignment:* `Rakho $arr[1] = "new_val";`

### 5. Falsy/Truthy Rules
The following values are evaluated as **falsy** by conditional structures:
* `Mithya` (Boolean False)
* `0` and `0.0` (Numeric zero)
* `""` (Empty string)
* `[]` (Empty array)

All other values are evaluated as **truthy**.

---

## 🛠️ Built-In Functions

Tacx.IR includes four built-in utility functions for essential computations:

### 1. `Lomba(x)`
Returns the length of a string or array.
* **Arguments**: Exactly 1.
* **Errors**: `TypeError` if `x` is not a string or array.
* **Example**:
  ```tacx
  Rakho $myList = [1, 2, 3];
  Bolo Lomba($myList); // Prints 3
  Bolo Lomba("Banglish"); // Prints 8
  ```

### 2. `Dhukao(arr, value)`
Appends `value` to the end of the mutable array `arr`. Returns the **new length** of the array.
* **Arguments**: Exactly 2 (an array and the value to append).
* **Errors**: `TypeError` if the first argument is not an array.
* **Example**:
  ```tacx
  Rakho $arr = [10];
  Rakho $newLen = Dhukao($arr, 20); // $arr is now [10, 20]
  Bolo $newLen; // Prints 2
  ```

### 3. `BerKoro(arr)`
Removes and returns the last element of the array `arr` (standard pop operation).
* **Arguments**: Exactly 1.
* **Errors**: `TypeError` if not an array, `RuntimeError` if the array is empty.
* **Example**:
  ```tacx
  Rakho $arr = [1, 2, 99];
  Rakho $lastVal = BerKoro($arr); // $arr is now [1, 2]
  Bolo $lastVal; // Prints 99
  ```

### 4. `Dhoron(x)`
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
  Bolo Dhoron(10.5);       // Prints "shonkha"
  Bolo Dhoron("test");     // Prints "lekha"
  Bolo Dhoron(Mithya);     // Prints "sotyo-mithya"
  ```

---

## 🎨 Syntax & Code Showcase

### 🔁 Fibonacci Sequence (Recursion & Conditions)
```tacx
// Recursive Fibonacci function
Dhori fibonacci(n) {
    Jodi n == 0 { Ferot 0; }
    Jodi n == 1 { Ferot 1; }
    Ferot fibonacci(n - 1) + fibonacci(n - 2);
}

Bolo "Fibonacci of 10 is:";
Bolo fibonacci(10); // Prints 55
```

### 🏎️ Complex Array & Loop Summation
```tacx
Dhori sumArray(arr, len) {
    Rakho $total = 0;
    Rakho $i = 0;
    Jotokhon $i < len {
        Rakho $total = $total + arr[$i];
        Rakho $i = $i + 1;
    }
    Ferot $total;
}

Rakho $nums = [10, 20, 30, 40];
Bolo sumArray($nums, Lomba($nums)); // Prints 100
```

### 🔁 While Loops with Break/Continue
```tacx
Rakho $k = 0;
Jotokhon $k < 10 {
    Rakho $k = $k + 1;
    
    // Skip 3 using continue
    Jodi $k == 3 {
        Chalano;
    }
    
    // Stop loop at 7 using break
    Jodi $k == 7 {
        Thamo;
    }
    
    Bolo $k;
}
// Outputs: 1, 2, 4, 5, 6
```

---

## 🏗️ Architecture & Project Layout

The compiler & interpreter modules are placed modularly in the [`tacxir`](tacxir/) package. Below is the file mapping:

* **[`tacxIR.py`](tacxIR.py)**: The main compatibility entry point. Preserves retro shell usages and maps to the underlying package APIs.
* **[`tacxir/__init__.py`](tacxir/__init__.py)**: Package initializer exposing public APIs (`Parser`, `TacxIR`, `tokenize`, `main`).
* **[`tacxir/tokens.py`](tacxir/tokens.py)**: High-performance regular expression tokenizer (Lexer), mapping code segments into positional tokens.
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
*Outputs tokens in format:*
```text
BOLO         Bolo
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
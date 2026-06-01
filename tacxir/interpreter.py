import io
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .ast_nodes import *
from .errors import TacxIRRuntimeError
from .parser import Parser
from .tokens import tokenize


class TacxIRControlFlow(BaseException):
    """Base class for Tacx.IR control-flow exceptions.
    Inherits from BaseException to prevent accidental catching by broad except Exception handlers."""
    pass


class ReturnException(TacxIRControlFlow):
    def __init__(self, value):
        self.value = value


class BreakException(TacxIRControlFlow):
    pass


class ContinueException(TacxIRControlFlow):
    pass


def is_number(val) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def is_truthy(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return val != ""
    if isinstance(val, list):
        return len(val) > 0
    return True


def _canon_name(name: str) -> str:
    return name[1:] if name.startswith("$") else name


def _source_line(source: str, line_no: int) -> str:
    if not source:
        return ""
    lines = source.split("\n")
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


class TacxIR:
    def __init__(self, source: str = ""):
        self.source = source
        self.globals: Dict[str, Any] = {}
        self.functions: Dict[str, DhoriStmt] = {}
        self.scopes: List[Dict[str, Any]] = [self.globals]
        self.current_node: Optional[ASTNode] = None
        self._last_error_node: Optional[ASTNode] = None
        self.function_depth = 0
        self.loop_depth = 0
        self.current_file: Optional[Path] = None
        self.imported_files: set = set()
        self.import_stack: List[Path] = []
        self.builtins: Dict[str, Callable[[List[Any]], Any]] = {
            # Length function
            "lomba": self._builtin_lomba,
            
            # Array push function
            "dhukao": self._builtin_dhukao,
            
            # Array pop function
            "berkoro": self._builtin_berkoro,
            
            # Type inspection function
            "dhoron": self._builtin_dhoron,
            
            # Math functions
            "mul": self._builtin_sqrt,
            "ghat": self._builtin_power,
            "boro": self._builtin_max,
            "choto": self._builtin_min,
            
            # String functions
            "bhag": self._builtin_split,
            "jora": self._builtin_join,
            "borhat": self._builtin_upper,
            "chothat": self._builtin_lower,
            
            # File I/O functions
            "porofile": self._builtin_read_file,
            "lekhofile": self._builtin_write_file,
            
            # Type conversion functions
            "shonkha": self._builtin_shonkha,
            "lekha": self._builtin_lekha,
            "purno": self._builtin_purno,
            "vashshonkha": self._builtin_vashshonkha,
        }

    def _make_runtime_error(self, message: str, node: Optional[ASTNode] = None) -> TacxIRRuntimeError:
        n = node or self.current_node
        line = n.line if n else None
        col = n.col if n else None
        sl = _source_line(self.source, line) if (line and self.source) else ""
        return TacxIRRuntimeError(message, line=line, col=col, source_line=sl)

    def _last_error_node_info(self) -> tuple:
        n = self._last_error_node or self.current_node
        if n and n.line is not None:
            return (n.line, n.col, _source_line(self.source, n.line))
        return (None, None, "")

    def _with_node(self, node: ASTNode, func):
        prev = self.current_node
        self.current_node = node
        try:
            return func()
        except BaseException:
            self._last_error_node = node
            raise
        finally:
            self.current_node = prev

    def _get_var(self, name: str):
        canon = _canon_name(name)
        for scope in reversed(self.scopes):
            if canon in scope:
                return scope[canon]
        raise NameError(f"Variable '{name}' is not defined")

    def _set_var(self, name: str, value):
        canon = _canon_name(name)
        for scope in reversed(self.scopes):
            if canon in scope:
                scope[canon] = value
                return
        self.scopes[-1][canon] = value

    def _declare_var(self, name: str, value):
        canon = _canon_name(name)
        self.scopes[-1][canon] = value

    def _push_scope(self):
        self.scopes.append({})

    def _pop_scope(self):
        if len(self.scopes) == 1:
            raise RuntimeError("Cannot pop the global scope")
        self.scopes.pop()

    def _execute_block(self, stmts: List[StmtNode]):
        self._push_scope()
        try:
            self.execute(stmts)
        finally:
            self._pop_scope()

    def _coerce_index(self, idx: Any) -> int:
        if isinstance(idx, bool) or not isinstance(idx, (int, float)):
            raise TypeError("Index must be an integer")
        if isinstance(idx, float):
            if not idx.is_integer():
                raise TypeError(f"Index must be an integer, got {idx}")
            idx = int(idx)
        return idx

    def _resolve_assignment_target(self, target: ASTNode):
        if isinstance(target, VarNode):
            return ("var", target.name)
        if isinstance(target, IndexNode):
            container = self.eval_expr(target.obj)
            if not isinstance(container, list):
                raise TypeError("Can only assign into arrays")
            idx = self._coerce_index(self.eval_expr(target.index))
            if idx < 0 or idx >= len(container):
                raise IndexError(f"Index {idx} out of bounds (length {len(container)})")
            return ("index", container, idx)
        raise RuntimeError(f"Invalid assignment target {type(target)}")

    def _assign_target(self, target: ASTNode, value: Any):
        resolved = self._resolve_assignment_target(target)
        if resolved[0] == "var":
            self._set_var(resolved[1], value)
            return value
        _, container, idx = resolved
        container[idx] = value
        return value

    def _expect_arity(self, name: str, args: List[Any], expected: int):
        if len(args) != expected:
            raise TypeError(f"Builtin '{name}' expects {expected} arguments, got {len(args)}")

    def _builtin_lomba(self, args: List[Any]) -> int:
        self._expect_arity("Lomba", args, 1)
        value = args[0]
        if not isinstance(value, (list, str)):
            raise TypeError("Lomba expects an array or string")
        return len(value)

    def _builtin_dhukao(self, args: List[Any]) -> int:
        self._expect_arity("Dhukao", args, 2)
        arr, value = args
        if not isinstance(arr, list):
            raise TypeError("Dhukao expects an array as the first argument")
        arr.append(value)
        return len(arr)

    def _builtin_berkoro(self, args: List[Any]) -> Any:
        self._expect_arity("BerKoro", args, 1)
        arr = args[0]
        if not isinstance(arr, list):
            raise TypeError("BerKoro expects an array")
        if not arr:
            raise RuntimeError("BerKoro cannot remove from an empty array")
        return arr.pop()

    def _builtin_dhoron(self, args: List[Any]) -> str:
        self._expect_arity("Dhoron", args, 1)
        value = args[0]
        if value is None:
            return "khali"
        if isinstance(value, bool):
            return "sotyo-mithya"
        if isinstance(value, (int, float)):
            return "shonkha"
        if isinstance(value, str):
            return "lekha"
        if isinstance(value, list):
            return "talika"
        return type(value).__name__

    def _builtin_sqrt(self, args: List[Any]) -> Any:
        self._expect_arity("mul", args, 1)
        val = args[0]
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return val
        raise TypeError("mul expects a number")

    def _builtin_power(self, args: List[Any]) -> Any:
        self._expect_arity("ghat", args, 2)
        base, exp = args
        if not is_number(base) or not is_number(exp):
            raise TypeError("ghat expects numbers")
        return base ** exp

    def _builtin_max(self, args: List[Any]) -> Any:
        self._expect_arity("boro", args, 2)
        a, b = args
        if not is_number(a) or not is_number(b):
            raise TypeError("boro expects numbers")
        return a if a > b else b

    def _builtin_min(self, args: List[Any]) -> Any:
        self._expect_arity("choto", args, 2)
        a, b = args
        if not is_number(a) or not is_number(b):
            raise TypeError("choto expects numbers")
        return a if a < b else b

    def _builtin_split(self, args: List[Any]) -> Any:
        self._expect_arity("bhag", args, 2)
        text, sep = args
        if not isinstance(text, str):
            raise TypeError("bhag expects a string as first argument")
        if not isinstance(sep, str):
            raise TypeError("bhag expects a string as second argument")
        return text.split(sep)

    def _builtin_join(self, args: List[Any]) -> Any:
        self._expect_arity("jora", args, 2)
        arr, sep = args
        if not isinstance(arr, list):
            raise TypeError("jora expects an array as first argument")
        if not isinstance(sep, str):
            raise TypeError("jora expects a string as second argument")
        return sep.join(str(e) for e in arr)

    def _builtin_upper(self, args: List[Any]) -> Any:
        self._expect_arity("borhat", args, 1)
        val = args[0]
        if not isinstance(val, str):
            raise TypeError("borhat expects a string")
        return val.upper()

    def _builtin_lower(self, args: List[Any]) -> Any:
        self._expect_arity("chothat", args, 1)
        val = args[0]
        if not isinstance(val, str):
            raise TypeError("chothat expects a string")
        return val.lower()

    def _builtin_read_file(self, args: List[Any]) -> Any:
        self._expect_arity("porofile", args, 1)
        path_str = args[0]
        if not isinstance(path_str, str):
            raise TypeError("porofile expects a string path")
        path = Path(path_str)
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")
        try:
            return path.read_text(encoding="utf-8")
        except PermissionError:
            raise PermissionError(f"Permission denied: {path}")

    def _builtin_write_file(self, args: List[Any]) -> Any:
        self._expect_arity("lekhofile", args, 2)
        path_str, content = args
        if not isinstance(path_str, str):
            raise TypeError("lekhofile expects a string path as first argument")
        if not isinstance(content, str):
            raise TypeError("lekhofile expects a string as second argument")
        path = Path(path_str)
        try:
            path.write_text(content, encoding="utf-8")
            return len(content)
        except PermissionError:
            raise PermissionError(f"Permission denied: {path}")

    def _builtin_shonkha(self, args: List[Any]) -> Any:
        """Convert value to number (shonkha)."""
        self._expect_arity("shonkha", args, 1)
        val = args[0]
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, (int, float)):
            return val
        if isinstance(val, str):
            try:
                if "." in val:
                    return float(val)
                return int(val)
            except ValueError:
                raise ValueError(f"Cannot convert '{val}' to number")
        raise TypeError(f"Cannot convert {type(val).__name__} to number")

    def _builtin_lekha(self, args: List[Any]) -> Any:
        """Convert value to string (lekha)."""
        self._expect_arity("lekha", args, 1)
        val = args[0]
        if val is None:
            return "khali"
        if isinstance(val, bool):
            return "sotyo" if val else "mithya"
        if isinstance(val, list):
            return "[" + ", ".join(str(e) for e in val) + "]"
        return str(val)

    def _builtin_purno(self, args: List[Any]) -> Any:
        """Convert value to integer (purno)."""
        self._expect_arity("purno", args, 1)
        val = args[0]
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, float):
            return int(val)
        if isinstance(val, int):
            return val
        if isinstance(val, str):
            try:
                return int(float(val))
            except ValueError:
                raise ValueError(f"Cannot convert '{val}' to integer")
        raise TypeError(f"Cannot convert {type(val).__name__} to integer")

    def _builtin_vashshonkha(self, args: List[Any]) -> Any:
        """Convert value to float (vashshonkha)."""
        self._expect_arity("vashshonkha", args, 1)
        val = args[0]
        if isinstance(val, bool):
            return 1.0 if val else 0.0
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            try:
                return float(val)
            except ValueError:
                raise ValueError(f"Cannot convert '{val}' to float")
        raise TypeError(f"Cannot convert {type(val).__name__} to float")

    def eval_expr(self, node: ASTNode) -> Any:
        def _eval():
            if isinstance(node, NumberNode):
                return node.value
            if isinstance(node, StringNode):
                return node.value
            if isinstance(node, BooleanNode):
                return node.value
            if isinstance(node, VarNode):
                return self._get_var(node.name)
            if isinstance(node, ArrayLiteralNode):
                return [self.eval_expr(e) for e in node.elements]
            if isinstance(node, IndexNode):
                obj = self.eval_expr(node.obj)
                if not isinstance(obj, list):
                    raise TypeError("Can only index arrays")
                idx = self._coerce_index(self.eval_expr(node.index))
                if idx < 0 or idx >= len(obj):
                    raise IndexError(f"Index {idx} out of bounds (length {len(obj)})")
                return obj[idx]
            if isinstance(node, SliceNode):
                obj = self.eval_expr(node.obj)
                if not isinstance(obj, (list, str)):
                    raise TypeError("Can only slice arrays or strings")
                start = None
                if node.start is not None:
                    start = self._coerce_index(self.eval_expr(node.start))
                stop = None
                if node.stop is not None:
                    stop = self._coerce_index(self.eval_expr(node.stop))
                return obj[start:stop]
            if isinstance(node, CallNode):
                # Case-sensitive function lookup
                func_name = node.name
                builtin = self.builtins.get(func_name)
                if builtin is not None:
                    args = [self.eval_expr(a) for a in node.args]
                    return builtin(args)
                func = self.functions.get(func_name)
                if func is None:
                    raise NameError(f"Function '{node.name}' not defined")
                args = [self.eval_expr(a) for a in node.args]
                if len(args) != len(func.params):
                    raise TypeError(f"Function '{node.name}' expects {len(func.params)} arguments, got {len(args)}")
                local_scope = {}
                for param, arg in zip(func.params, args):
                    local_scope[_canon_name(param)] = arg
                self.scopes.append(local_scope)
                self.function_depth += 1
                try:
                    self.execute(func.body)
                    return None
                except ReturnException as ret:
                    return ret.value
                finally:
                    self.function_depth -= 1
                    self.scopes.pop()
            if isinstance(node, UnaryOpNode):
                val = self.eval_expr(node.operand)
                if node.op == "-":
                    if not is_number(val):
                        raise TypeError(f"Unary '-' requires number, got {type(val).__name__}")
                    return -val
                elif node.op == "!":
                    return not is_truthy(val)
            if isinstance(node, BinOpNode):
                left = self.eval_expr(node.left)
                op = node.op
                if op in ("ebong", "ar"):
                    return is_truthy(left) and is_truthy(self.eval_expr(node.right))
                if op in ("othoba", "ba"):
                    return is_truthy(left) or is_truthy(self.eval_expr(node.right))
                right = self.eval_expr(node.right)
                if op == "+":
                    if isinstance(left, str) or isinstance(right, str):
                        return str(left) + str(right)
                    if not is_number(left) or not is_number(right):
                        raise TypeError("Operator '+' requires numbers when not concatenating strings")
                    return left + right
                elif op in ("-", "*", "/", "%"):
                    if not is_number(left) or not is_number(right):
                        raise TypeError(f"Operator '{op}' requires numbers")
                    if op == "-":
                        return left - right
                    if op == "*":
                        return left * right
                    if op == "/":
                        if right == 0:
                            raise ZeroDivisionError("Division by zero")
                        return left / right
                    if op == "%":
                        if right == 0:
                            raise ZeroDivisionError("Modulo by zero")
                        return left % right
                elif op in ("==", "!=", "<", ">", "<=", ">="):
                    is_left_num = is_number(left)
                    is_right_num = is_number(right)

                    if op in ("==", "!="):
                        return (left == right) if op == "==" else (left != right)

                    if is_left_num and is_right_num:
                        lv, rv = left, right
                    elif type(left) is type(right) and isinstance(left, str):
                        lv, rv = left, right
                    else:
                        raise TypeError(
                            f"Operator '{op}' requires comparable values of the same type, got "
                            f"{type(left).__name__} and {type(right).__name__}"
                        )

                    if op == "<":
                        return lv < rv
                    if op == ">":
                        return lv > rv
                    if op == "<=":
                        return lv <= rv
                    if op == ">=":
                        return lv >= rv
                else:
                    raise RuntimeError(f"Unknown operator '{op}'")
            raise RuntimeError(f"Unknown expression node {type(node)}")
        return self._with_node(node, _eval)

    def execute(self, stmts: List[StmtNode]):
        for stmt in stmts:
            if isinstance(stmt, BoloStmt):
                print(self.eval_expr(stmt.expr))
            elif isinstance(stmt, PoroStmt):
                inp = input()
                try:
                    if "." in inp:
                        val = float(inp)
                    else:
                        val = int(inp)
                except ValueError:
                    val = inp
                self._set_var(stmt.var_name, val)
            elif isinstance(stmt, RakhoStmt):
                self._assign_target(stmt.target, self.eval_expr(stmt.expr))
            elif isinstance(stmt, JodiStmt):
                if is_truthy(self.eval_expr(stmt.cond)):
                    self._execute_block(stmt.true_body)
                elif stmt.false_body:
                    self._execute_block(stmt.false_body)
            elif isinstance(stmt, CholaoStmt):
                count = self.eval_expr(stmt.count)
                if isinstance(count, bool) or not isinstance(count, (int, float)):
                    raise TypeError("Cholao count must be a non-negative integer")
                if isinstance(count, float) and not count.is_integer():
                    raise TypeError("Cholao count must be a non-negative integer")
                if count < 0:
                    raise ValueError("Cholao count must be non-negative")
                self.loop_depth += 1
                try:
                    for _ in range(int(count)):
                        try:
                            self._execute_block(stmt.body)
                        except BreakException:
                            break
                        except ContinueException:
                            continue
                finally:
                    self.loop_depth -= 1
            elif isinstance(stmt, JotokhonStmt):
                self.loop_depth += 1
                try:
                    while is_truthy(self.eval_expr(stmt.cond)):
                        try:
                            self._execute_block(stmt.body)
                        except BreakException:
                            break
                        except ContinueException:
                            continue
                finally:
                    self.loop_depth -= 1
            elif isinstance(stmt, DhoriStmt):
                if stmt.name in self.functions:
                    raise RuntimeError(f"Function '{stmt.name}' already defined")
                self.functions[stmt.name] = stmt
            elif isinstance(stmt, DaoStmt):
                if self.function_depth == 0:
                    raise RuntimeError("Dao can only be used inside a function")
                val = self.eval_expr(stmt.expr)
                raise ReturnException(val)
            elif isinstance(stmt, ThamoStmt):
                if self.loop_depth == 0:
                    raise RuntimeError("Thamo can only be used inside a loop")
                raise BreakException()
            elif isinstance(stmt, ChalanoStmt):
                if self.loop_depth == 0:
                    raise RuntimeError("Chalano can only be used inside a loop")
                raise ContinueException()
            elif isinstance(stmt, AmdoStmt):
                self._execute_import(stmt)
            elif isinstance(stmt, AugAssignStmt):
                self._execute_augmented_assignment(stmt)
            elif isinstance(stmt, IncDecStmt):
                self._execute_inc_dec(stmt)
            elif isinstance(stmt, ExprStmt):
                self.eval_expr(stmt.expr)
            else:
                raise RuntimeError(f"Unknown statement {type(stmt)}")

    def _execute_augmented_assignment(self, stmt: AugAssignStmt):
        """Execute augmented assignment (e.g., $x += 5, $y -= 3)."""
        current_value = self.eval_expr(stmt.target)
        new_value = self.eval_expr(stmt.value)
        
        # Map operator to operation
        op = stmt.op
        if op == "+=":
            if isinstance(current_value, str) or isinstance(new_value, str):
                result = str(current_value) + str(new_value)
            elif is_number(current_value) and is_number(new_value):
                result = current_value + new_value
            else:
                raise TypeError(f"Operator '+=' requires numbers or strings, got {type(current_value).__name__} and {type(new_value).__name__}")
        elif op == "-=":
            if not is_number(current_value) or not is_number(new_value):
                raise TypeError(f"Operator '-=' requires numbers, got {type(current_value).__name__} and {type(new_value).__name__}")
            result = current_value - new_value
        elif op == "*=":
            if not is_number(current_value) or not is_number(new_value):
                raise TypeError(f"Operator '*=' requires numbers, got {type(current_value).__name__} and {type(new_value).__name__}")
            result = current_value * new_value
        elif op == "/=":
            if not is_number(current_value) or not is_number(new_value):
                raise TypeError(f"Operator '/=' requires numbers, got {type(current_value).__name__} and {type(new_value).__name__}")
            if new_value == 0:
                raise ZeroDivisionError("Division by zero")
            result = current_value / new_value
        elif op == "%=":
            if not is_number(current_value) or not is_number(new_value):
                raise TypeError(f"Operator '%=' requires numbers, got {type(current_value).__name__} and {type(new_value).__name__}")
            if new_value == 0:
                raise ZeroDivisionError("Modulo by zero")
            result = current_value % new_value
        else:
            raise RuntimeError(f"Unknown augmented assignment operator '{op}'")
        
        self._assign_target(stmt.target, result)

    def _execute_inc_dec(self, stmt: IncDecStmt):
        """Execute increment/decrement (e.g., $x++, $y--)."""
        current_value = self.eval_expr(stmt.target)
        if not is_number(current_value):
            raise TypeError(f"Operator '{stmt.op}' requires a number, got {type(current_value).__name__}")
        
        if stmt.op == "++":
            new_value = current_value + 1
        elif stmt.op == "--":
            new_value = current_value - 1
        else:
            raise RuntimeError(f"Unknown increment/decrement operator '{stmt.op}'")
        
        self._assign_target(stmt.target, new_value)

    def _execute_import(self, stmt: AmdoStmt):
        if self.current_file is None:
            raise RuntimeError("amdo can only be used relative to a source file")
        base_dir = self.current_file.resolve().parent
        import_path = Path(stmt.path)
        if not import_path.suffix:
            import_path = import_path.with_suffix(".tacx")
        resolved = (base_dir / import_path).resolve()
        if resolved in self.import_stack:
            raise RuntimeError(f"Circular import detected: {resolved}")
        if resolved not in self.imported_files:
            if not resolved.is_file():
                raise FileNotFoundError(f"Import file not found: {resolved}")
            self.import_stack.append(resolved)
            try:
                imported_source = resolved.read_text(encoding="utf-8")
                tokens, src = tokenize(imported_source)
                parser = Parser(tokens, src)
                imported_program = parser.parse_program()
                prev_file = self.current_file
                prev_source = self.source
                self.current_file = resolved
                self.source = imported_source
                self.imported_files.add(resolved)
                try:
                    self.execute(imported_program)
                finally:
                    self.current_file = prev_file
                    self.source = prev_source
            finally:
                self.import_stack.pop()

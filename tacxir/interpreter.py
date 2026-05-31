from typing import Any, Callable, Dict, List

from .ast_nodes import *


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


class TacxIR:
    def __init__(self):
        self.globals: Dict[str, Any] = {}
        self.functions: Dict[str, DhoriStmt] = {}
        self.scopes: List[Dict[str, Any]] = [self.globals]
        self.function_depth = 0
        self.loop_depth = 0
        self.builtins: Dict[str, Callable[[List[Any]], Any]] = {
            "Lomba": self._builtin_lomba,
            "lomba": self._builtin_lomba,
            "Dhukao": self._builtin_dhukao,
            "dhukao": self._builtin_dhukao,
            "dhuk": self._builtin_dhukao,
            "BerKoro": self._builtin_berkoro,
            "berkoro": self._builtin_berkoro,
            "berkr": self._builtin_berkoro,
            "Dhoron": self._builtin_dhoron,
            "dhoron": self._builtin_dhoron,
            "dhron": self._builtin_dhoron,
        }

    def _get_var(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise NameError(f"Variable '{name}' is not defined")

    def _set_var(self, name: str, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        self.scopes[-1][name] = value

    def _declare_var(self, name: str, value):
        self.scopes[-1][name] = value

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

    def eval_expr(self, node: ASTNode) -> Any:
        if isinstance(node, NumberNode):
            return node.value
        if isinstance(node, StringNode):
            return node.value
        if isinstance(node, BooleanNode):
            return node.value
        if isinstance(node, VarNode):
            if node.name.startswith("$"):
                return self._get_var(node.name)
            # Bare identifier: try function param / scope lookup
            for scope in reversed(self.scopes):
                if node.name in scope:
                    return scope[node.name]
            raise NameError(
                f"'{node.name}' is not defined. Variables must start with '$' (e.g., '${node.name}')."
            )
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
        if isinstance(node, CallNode):
            builtin = self.builtins.get(node.name)
            if builtin is not None:
                args = [self.eval_expr(a) for a in node.args]
                return builtin(args)
            func = self.functions.get(node.name)
            if func is None:
                raise NameError(f"Function '{node.name}' not defined")
            args = [self.eval_expr(a) for a in node.args]
            if len(args) != len(func.params):
                raise TypeError(f"Function '{node.name}' expects {len(func.params)} arguments, got {len(args)}")
            local_scope = {}
            for param, arg in zip(func.params, args):
                local_scope[param] = arg
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
            elif isinstance(stmt, ExprStmt):
                self.eval_expr(stmt.expr)
            else:
                raise RuntimeError(f"Unknown statement {type(stmt)}")


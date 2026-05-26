from typing import List, Union


class ASTNode:
    pass


class NumberNode(ASTNode):
    def __init__(self, value: Union[int, float]):
        self.value = value


class StringNode(ASTNode):
    def __init__(self, value: str):
        self.value = value


class VarNode(ASTNode):
    def __init__(self, name: str):
        self.name = name


class BooleanNode(ASTNode):
    def __init__(self, value: bool):
        self.value = value


class BinOpNode(ASTNode):
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op = op
        self.left = left
        self.right = right


class UnaryOpNode(ASTNode):
    def __init__(self, op: str, operand: ASTNode):
        self.op = op
        self.operand = operand


class ArrayLiteralNode(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements


class IndexNode(ASTNode):
    def __init__(self, obj: ASTNode, index: ASTNode):
        self.obj = obj
        self.index = index


class CallNode(ASTNode):
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args


class StmtNode:
    pass


class BoloStmt(StmtNode):
    def __init__(self, expr):
        self.expr = expr


class PoroStmt(StmtNode):
    def __init__(self, var_name):
        self.var_name = var_name


class RakhoStmt(StmtNode):
    def __init__(self, target, expr):
        self.target = target
        self.expr = expr


class JodiStmt(StmtNode):
    def __init__(self, cond, true_body, false_body):
        self.cond = cond
        self.true_body = true_body
        self.false_body = false_body


class CholaoStmt(StmtNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body


class JotokhonStmt(StmtNode):
    def __init__(self, cond, body):
        self.cond = cond
        self.body = body


class DhoriStmt(StmtNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body


class FerotStmt(StmtNode):
    def __init__(self, expr):
        self.expr = expr


class ThamoStmt(StmtNode):
    pass


class ChalanoStmt(StmtNode):
    pass


class ExprStmt(StmtNode):
    def __init__(self, expr):
        self.expr = expr


def ast_to_debug_lines(node: ASTNode, indent: int = 0) -> List[str]:
    pad = "  " * indent
    if isinstance(node, NumberNode):
        return [f"{pad}Number({node.value})"]
    if isinstance(node, StringNode):
        return [f"{pad}String({node.value!r})"]
    if isinstance(node, BooleanNode):
        return [f"{pad}Boolean({node.value})"]
    if isinstance(node, VarNode):
        return [f"{pad}Var({node.name})"]
    if isinstance(node, UnaryOpNode):
        lines = [f"{pad}UnaryOp({node.op})"]
        lines.extend(ast_to_debug_lines(node.operand, indent + 1))
        return lines
    if isinstance(node, BinOpNode):
        lines = [f"{pad}BinOp({node.op})"]
        lines.extend(ast_to_debug_lines(node.left, indent + 1))
        lines.extend(ast_to_debug_lines(node.right, indent + 1))
        return lines
    if isinstance(node, ArrayLiteralNode):
        lines = [f"{pad}ArrayLiteral"]
        for element in node.elements:
            lines.extend(ast_to_debug_lines(element, indent + 1))
        return lines
    if isinstance(node, IndexNode):
        lines = [f"{pad}Index"]
        lines.extend(ast_to_debug_lines(node.obj, indent + 1))
        lines.extend(ast_to_debug_lines(node.index, indent + 1))
        return lines
    if isinstance(node, CallNode):
        lines = [f"{pad}Call({node.name})"]
        for arg in node.args:
            lines.extend(ast_to_debug_lines(arg, indent + 1))
        return lines
    if isinstance(node, BoloStmt):
        lines = [f"{pad}BoloStmt"]
        lines.extend(ast_to_debug_lines(node.expr, indent + 1))
        return lines
    if isinstance(node, PoroStmt):
        return [f"{pad}PoroStmt({node.var_name})"]
    if isinstance(node, RakhoStmt):
        lines = [f"{pad}RakhoStmt"]
        lines.extend(ast_to_debug_lines(node.target, indent + 1))
        lines.extend(ast_to_debug_lines(node.expr, indent + 1))
        return lines
    if isinstance(node, JodiStmt):
        lines = [f"{pad}JodiStmt"]
        lines.append(f"{pad}  Condition:")
        lines.extend(ast_to_debug_lines(node.cond, indent + 2))
        lines.append(f"{pad}  TrueBody:")
        for stmt in node.true_body:
            lines.extend(ast_to_debug_lines(stmt, indent + 2))
        if node.false_body:
            lines.append(f"{pad}  FalseBody:")
            for stmt in node.false_body:
                lines.extend(ast_to_debug_lines(stmt, indent + 2))
        return lines
    if isinstance(node, CholaoStmt):
        lines = [f"{pad}CholaoStmt"]
        lines.extend(ast_to_debug_lines(node.count, indent + 1))
        for stmt in node.body:
            lines.extend(ast_to_debug_lines(stmt, indent + 1))
        return lines
    if isinstance(node, JotokhonStmt):
        lines = [f"{pad}JotokhonStmt"]
        lines.extend(ast_to_debug_lines(node.cond, indent + 1))
        for stmt in node.body:
            lines.extend(ast_to_debug_lines(stmt, indent + 1))
        return lines
    if isinstance(node, DhoriStmt):
        lines = [f"{pad}DhoriStmt({node.name}, params={node.params})"]
        for stmt in node.body:
            lines.extend(ast_to_debug_lines(stmt, indent + 1))
        return lines
    if isinstance(node, FerotStmt):
        lines = [f"{pad}FerotStmt"]
        lines.extend(ast_to_debug_lines(node.expr, indent + 1))
        return lines
    if isinstance(node, ThamoStmt):
        return [f"{pad}ThamoStmt"]
    if isinstance(node, ChalanoStmt):
        return [f"{pad}ChalanoStmt"]
    if isinstance(node, ExprStmt):
        lines = [f"{pad}ExprStmt"]
        lines.extend(ast_to_debug_lines(node.expr, indent + 1))
        return lines
    return [f"{pad}{type(node).__name__}"]


def tokens_to_lines(tokens):
    return [f"{token.type:<12} {token.value}" for token in tokens]


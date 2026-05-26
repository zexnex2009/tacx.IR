from typing import List, Optional

from .ast_nodes import *
from .tokens import Token


class Parser:
    def __init__(self, tokens: List[Token], source: str):
        self.tokens = tokens
        self.pos = 0
        self.source = source

    def _error(self, msg: str, token: Optional[Token] = None):
        if token:
            from .tokens import pos_to_linecol
            line, col = pos_to_linecol(self.source, token.pos)
            raise SyntaxError(f"{msg} at line {line}, col {col} (token {token.type} '{token.value}')")
        raise SyntaxError(msg)

    def peek(self) -> Optional[Token]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected: Optional[str] = None) -> Token:
        tok = self.peek()
        if tok is None:
            self._error("Unexpected end of input")
        if expected and tok.type != expected:
            self._error(f"Expected {expected}, got {tok.type}", tok)
        self.pos += 1
        return tok

    def decode_string_literal(self, token: Token) -> str:
        raw = token.value[1:-1]
        escapes = {"\\n": "\n", "\\t": "\t", "\\r": "\r", '\\"': '"', "\\\\": "\\"}
        decoded = []
        i = 0
        while i < len(raw):
            if raw[i] != "\\":
                decoded.append(raw[i])
                i += 1
                continue
            if i + 1 >= len(raw):
                self._error("Unterminated escape sequence in string literal", token)
            seq = raw[i : i + 2]
            if seq not in escapes:
                self._error(f"Unsupported escape sequence {seq!r}", token)
            decoded.append(escapes[seq])
            i += 2
        return "".join(decoded)

    def parse_assignment_target(self) -> ASTNode:
        if self.peek() is None or self.peek().type not in ("VAR", "ID"):
            self._error("Expected variable or identifier after Rakho", self.peek())
        target = VarNode(self.consume().value)
        while self.peek() and self.peek().type == "LBRACKET":
            self.consume("LBRACKET")
            index = self.parse_expression()
            self.consume("RBRACKET")
            target = IndexNode(target, index)
        return target

    def parse_expression(self) -> ASTNode:
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek() and self.peek().type == "OTHOBA":
            op = self.consume().value
            right = self.parse_and()
            left = BinOpNode(op, left, right)
        return left

    def parse_and(self):
        left = self.parse_comparison()
        while self.peek() and self.peek().type == "EBONG":
            op = self.consume().value
            right = self.parse_comparison()
            left = BinOpNode(op, left, right)
        return left

    def parse_comparison(self):
        left = self.parse_additive()
        while self.peek() and self.peek().type in ("EQEQ", "NOTEQ", "LT", "GT", "LTE", "GTE"):
            op = self.consume().value
            right = self.parse_additive()
            left = BinOpNode(op, left, right)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.peek() and self.peek().type in ("PLUS", "MINUS"):
            op = self.consume().value
            right = self.parse_multiplicative()
            left = BinOpNode(op, left, right)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.peek() and self.peek().type in ("MUL", "DIV", "MOD"):
            op = self.consume().value
            right = self.parse_unary()
            left = BinOpNode(op, left, right)
        return left

    def parse_unary(self):
        if self.peek() and self.peek().type == "MINUS":
            self.consume("MINUS")
            operand = self.parse_unary()
            return UnaryOpNode("-", operand)
        if self.peek() and self.peek().type == "NA":
            self.consume("NA")
            operand = self.parse_unary()
            return UnaryOpNode("!", operand)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            tok = self.peek()
            if tok and tok.type == "LBRACKET":
                self.consume("LBRACKET")
                index = self.parse_expression()
                self.consume("RBRACKET")
                expr = IndexNode(expr, index)
            elif tok and tok.type == "LPAREN":
                if not isinstance(expr, VarNode) and not hasattr(expr, "name"):
                    self._error("Only identifiers or variables can be called", tok)
                name = expr.name if isinstance(expr, VarNode) else expr.name
                self.consume("LPAREN")
                args = []
                if self.peek() and self.peek().type != "RPAREN":
                    args.append(self.parse_expression())
                    while self.peek() and self.peek().type == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expression())
                self.consume("RPAREN")
                expr = CallNode(name, args)
            else:
                break
        return expr

    def parse_primary(self) -> ASTNode:
        tok = self.peek()
        if tok is None:
            self._error("Unexpected end of expression")
        if tok.type == "NUMBER":
            self.consume()
            raw = tok.value
            return NumberNode(float(raw) if "." in raw else int(raw))
        elif tok.type == "STRING":
            self.consume()
            return StringNode(self.decode_string_literal(tok))
        elif tok.type == "SOTYO":
            self.consume()
            return BooleanNode(True)
        elif tok.type == "MITHYA":
            self.consume()
            return BooleanNode(False)
        elif tok.type == "VAR":
            self.consume()
            return VarNode(tok.value)
        elif tok.type == "ID":
            self.consume()
            return VarNode(tok.value)
        elif tok.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expression()
            self.consume("RPAREN")
            return expr
        elif tok.type == "LBRACKET":
            self.consume("LBRACKET")
            elements = []
            if self.peek() and self.peek().type != "RBRACKET":
                elements.append(self.parse_expression())
                while self.peek() and self.peek().type == "COMMA":
                    self.consume("COMMA")
                    elements.append(self.parse_expression())
            self.consume("RBRACKET")
            return ArrayLiteralNode(elements)
        else:
            self._error(f"Unexpected token {tok.type} in expression", tok)

    def parse_statement(self) -> Optional[StmtNode]:
        tok = self.peek()
        if tok is None:
            return None
        if tok.type == "BOLO":
            self.consume("BOLO")
            expr = self.parse_expression()
            self.consume("SEMI")
            return BoloStmt(expr)
        elif tok.type == "PORO":
            self.consume("PORO")
            var = self.consume("VAR") if self.peek().type == "VAR" else self.consume("ID")
            self.consume("SEMI")
            return PoroStmt(var.value)
        elif tok.type == "RAKHO":
            self.consume("RAKHO")
            target = self.parse_assignment_target()
            self.consume("EQ")
            expr = self.parse_expression()
            self.consume("SEMI")
            return RakhoStmt(target, expr)
        elif tok.type == "JODI":
            self.consume("JODI")
            cond = self.parse_expression()
            self.consume("LBRACE")
            true_body = self.parse_block()
            false_body = []
            if self.peek() and self.peek().type == "NAILE":
                self.consume("NAILE")
                self.consume("LBRACE")
                false_body = self.parse_block()
            return JodiStmt(cond, true_body, false_body)
        elif tok.type == "CHOLAO":
            self.consume("CHOLAO")
            count_expr = self.parse_expression()
            self.consume("BAR")
            self.consume("LBRACE")
            body = self.parse_block()
            return CholaoStmt(count_expr, body)
        elif tok.type == "JOTOKHON":
            self.consume("JOTOKHON")
            cond = self.parse_expression()
            self.consume("LBRACE")
            body = self.parse_block()
            return JotokhonStmt(cond, body)
        elif tok.type == "DHORI":
            self.consume("DHORI")
            name = self.consume("ID").value
            self.consume("LPAREN")
            params = []
            if self.peek() and self.peek().type != "RPAREN":
                params.append(self.consume("ID").value)
                while self.peek() and self.peek().type == "COMMA":
                    self.consume("COMMA")
                    params.append(self.consume("ID").value)
            self.consume("RPAREN")
            self.consume("LBRACE")
            body = self.parse_block()
            return DhoriStmt(name, params, body)
        elif tok.type == "FEROT":
            self.consume("FEROT")
            expr = self.parse_expression()
            self.consume("SEMI")
            return FerotStmt(expr)
        elif tok.type == "THAMO":
            self.consume("THAMO")
            self.consume("SEMI")
            return ThamoStmt()
        elif tok.type == "CHALANO":
            self.consume("CHALANO")
            self.consume("SEMI")
            return ChalanoStmt()
        elif tok.type == "SEMI":
            self.consume("SEMI")
            return None
        else:
            expr = self.parse_expression()
            self.consume("SEMI")
            return ExprStmt(expr)

    def parse_block(self) -> List[StmtNode]:
        stmts = []
        while self.peek() and self.peek().type != "RBRACE":
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        self.consume("RBRACE")
        return stmts

    def parse_program(self) -> List[StmtNode]:
        program = []
        while self.peek() is not None:
            stmt = self.parse_statement()
            if stmt is not None:
                program.append(stmt)
        return program


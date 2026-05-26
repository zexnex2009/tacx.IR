import re


def keyword_pattern(keyword: str) -> str:
    return rf"{keyword}\b"


TOKEN_TYPES = [
    ("DHORI", keyword_pattern("Dhori")),
    ("FEROT", keyword_pattern("Ferot")),
    ("JOTOKHON", keyword_pattern("Jotokhon")),
    ("THAMO", keyword_pattern("Thamo")),
    ("CHALANO", keyword_pattern("Chalano")),
    ("SOTYO", keyword_pattern("Sotyo")),
    ("MITHYA", keyword_pattern("Mithya")),
    ("EBONG", keyword_pattern("Ebong")),
    ("OTHOBA", keyword_pattern("Othoba")),
    ("NAILE", keyword_pattern("Naile")),
    ("NA", keyword_pattern("Na")),
    ("CHOLAO", keyword_pattern("Cholao")),
    ("BAR", keyword_pattern("bar")),
    ("JODI", keyword_pattern("Jodi")),
    ("BOLO", keyword_pattern("Bolo")),
    ("PORO", keyword_pattern("Poro")),
    ("RAKHO", keyword_pattern("Rakho")),
    ("SKIP", r"[ \t\r\n]+"),
    ("COMMENT", r"//.*"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("EQEQ", r"=="),
    ("NOTEQ", r"!="),
    ("LTE", r"<="),
    ("GTE", r">="),
    ("EQ", r"="),
    ("LT", r"<"),
    ("GT", r">"),
    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("MUL", r"\*"),
    ("MOD", r"%"),
    ("DIV", r"/"),
    ("SEMI", r";"),
    ("STRING", r'"([^"\\]|\\.)*"'),
    ("NUMBER", r"\d+(\.\d+)?"),
    ("VAR", r"\$[a-zA-Z_][a-zA-Z0-9_]*"),
    ("ID", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("MISMATCH", r"."),
]


TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES)


class Token:
    __slots__ = ("type", "value", "pos")

    def __init__(self, type_: str, value: str, pos: int):
        self.type = type_
        self.value = value
        self.pos = pos

    def __repr__(self):
        return f"Token({self.type}, {self.value!r})"


def pos_to_linecol(code: str, pos: int):
    line = code.count("\n", 0, pos) + 1
    last_nl = code.rfind("\n", 0, pos)
    col = pos - last_nl if last_nl != -1 else pos + 1
    return line, col


def tokenize(code: str):
    tokens = []
    for mo in re.finditer(TOKEN_REGEX, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ("SKIP", "COMMENT"):
            continue
        if kind == "MISMATCH":
            line, col = pos_to_linecol(code, mo.start())
            raise SyntaxError(f"Unexpected character {value!r} at line {line}, column {col}")
        tokens.append(Token(kind, value, mo.start()))
    return tokens, code


import re


def keyword_pattern(keyword: str) -> str:
    return rf"(?:{keyword})\b"


ALIASES = {
    "JOTOKHON": ("jtkhn", "jotokhon"),
    "THAMO": ("tham", "thamo"),
    "CHALANO": ("chal", "chalano"),
    "EBONG": ("ar", "ebong"),
    "OTHOBA": ("ba", "othoba"),
    "CHOLAO": ("kor", "cholao"),
    "DHUKAO": ("dhuk", "dhukao"),
    "BERKORO": ("berkr", "berkoro"),
    "DHORON": ("dhron", "dhoron"),
}


TOKEN_TYPES = [
    ("DHORI", keyword_pattern("dhori")),
    ("FEROT", keyword_pattern("dao")),
    ("JOTOKHON", keyword_pattern("jtkhn|jotokhon")),
    ("THAMO", keyword_pattern("tham|thamo")),
    ("CHALANO", keyword_pattern("chal|chalano")),
    ("SOTYO", keyword_pattern("sotyo")),
    ("MITHYA", keyword_pattern("mithya")),
    ("EBONG", keyword_pattern("ar|ebong")),
    ("OTHOBA", keyword_pattern("ba|othoba")),
    ("NAILE", keyword_pattern("naile")),
    ("NA", keyword_pattern("na")),
    ("CHOLAO", keyword_pattern("kor|cholao")),
    ("BAR", keyword_pattern("bar")),
    ("JODI", keyword_pattern("jodi")),
    ("BOLO", keyword_pattern("bolo")),
    ("PORO", keyword_pattern("poro")),
    ("RAKHO", keyword_pattern("rakho")),
    ("AMDO", keyword_pattern("amdo")),
    ("SKIP", r"[ \t\r\n]+"),
    ("COMMENT", r"//.*"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("COLON", r":"),
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


TOKEN_REGEX = re.compile("|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_TYPES), re.IGNORECASE)
KEYWORD_TOKEN_TYPES = {
    "DHORI", "FEROT", "JOTOKHON", "THAMO", "CHALANO",
    "SOTYO", "MITHYA", "EBONG", "OTHOBA", "NAILE",
    "NA", "CHOLAO", "BAR", "JODI", "BOLO", "PORO", "RAKHO", "AMDO",
}


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
    for mo in TOKEN_REGEX.finditer(code):
        kind = mo.lastgroup
        value = mo.group()
        if kind in ("SKIP", "COMMENT"):
            continue
        if kind in KEYWORD_TOKEN_TYPES:
            value = value.lower()
        if kind == "MISMATCH":
            line, col = pos_to_linecol(code, mo.start())
            raise SyntaxError(f"Unexpected character {value!r} at line {line}, column {col}")
        tokens.append(Token(kind, value, mo.start()))
    return tokens, code

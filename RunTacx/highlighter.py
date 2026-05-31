from __future__ import annotations

import re

try:
    from PyQt6.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter
except ImportError:  # pragma: no cover - exercised only when PyQt6 is unavailable
    from PyQt5.QtGui import QColor, QFont, QTextCharFormat, QSyntaxHighlighter


def _format(color: str, bold: bool = False, italic: bool = False) -> QTextCharFormat:
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold if hasattr(QFont, "Weight") else QFont.Bold)
    fmt.setFontItalic(italic)
    return fmt


class TacxSyntaxHighlighter(QSyntaxHighlighter):
    KEYWORDS = {
        "rakho",
        "bolo",
        "poro",
        "jodi",
        "naile",
        "jtkhn",
        "jotokhon",
        "kor",
        "cholao",
        "bar",
        "dhori",
        "dao",
        "tham",
        "thamo",
        "chal",
        "chalano",
        "amdo",
    }
    OPERATORS = {"ar", "ebong", "ba", "othoba", "na"}
    BUILTINS = {
        "lomba", "dhukao", "dhuk", "berkoro", "berkr", "dhoron", "dhron",
        "mul", "ghat", "boro", "choto",
        "bhag", "jora", "borhat", "chothat",
        "porofile", "lekhofile",
    }

    def __init__(self, document):
        super().__init__(document)
        self.rules: list[tuple[re.Pattern[str], QTextCharFormat]] = []
        self._build_rules()

    def _pattern(self, value: str) -> re.Pattern[str]:
        return re.compile(rf"\b{re.escape(value)}\b", re.IGNORECASE)

    def _build_rules(self):
        keyword_fmt = _format("#ff9f43", bold=True)
        builtin_fmt = _format("#54a0ff", bold=True)
        string_fmt = _format("#2ecc71")
        comment_fmt = _format("#8c8c8c", italic=True)
        number_fmt = _format("#f368e0")
        operator_fmt = _format("#ff6b6b", bold=True)

        for word in sorted(self.KEYWORDS):
            self.rules.append((self._pattern(word), keyword_fmt))
        for word in sorted(self.BUILTINS):
            self.rules.append((self._pattern(word), builtin_fmt))
        for word in sorted(self.OPERATORS):
            self.rules.append((self._pattern(word), operator_fmt))

        self.rules.extend(
            [
                (re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"', re.IGNORECASE), string_fmt),
                (re.compile(r"//[^\n]*"), comment_fmt),
                (re.compile(r"\b\d+(\.\d+)?\b"), number_fmt),
            ]
        )

    def highlightBlock(self, text: str):
        for pattern, fmt in self.rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)

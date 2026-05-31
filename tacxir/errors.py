from .tokens import pos_to_linecol


class TacxIRError(RuntimeError):
    pass


class TacxIRRuntimeError(TacxIRError):
    def __init__(self, message, *, line=None, col=None, source_line=""):
        super().__init__(message)
        self.line = line
        self.col = col
        self.source_line = source_line

    def format(self):
        parts = [str(self)]
        if self.line is not None:
            parts.insert(0, f"line {self.line}")
        if self.col is not None:
            parts.insert(0, f"col {self.col}")
        if self.source_line:
            parts.append(f"\n    {self.source_line}")
        if self.line is not None or self.col is not None:
            header = f"RuntimeError at line {self.line}, col {self.col}"
            body = str(self)
            return f"{header}: {body}{self._source_excerpt()}"
        return str(self)

    def _source_excerpt(self):
        if not self.source_line:
            return ""
        return f"\n    {self.source_line}"


def format_tacx_error(exc: TacxIRRuntimeError) -> str:
    return exc.format()

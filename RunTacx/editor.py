from __future__ import annotations

try:
    from PyQt6.QtCore import QSize, Qt, QRect
    from PyQt6.QtGui import QColor, QPainter, QTextCharFormat
    from PyQt6.QtWidgets import QPlainTextEdit, QTextEdit, QWidget
    PYQT6 = True
    ALIGN_RIGHT = Qt.AlignmentFlag.AlignRight
except ImportError:  # pragma: no cover - exercised only when PyQt6 is unavailable
    from PyQt5.QtCore import QSize, Qt, QRect
    from PyQt5.QtGui import QColor, QPainter, QTextCharFormat
    from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit, QWidget
    PYQT6 = False
    ALIGN_RIGHT = Qt.AlignRight


def _font_advance(editor: QPlainTextEdit, text: str) -> int:
    metrics = editor.fontMetrics()
    if hasattr(metrics, "horizontalAdvance"):
        return metrics.horizontalAdvance(text)
    return metrics.width(text)  # type: ignore[attr-defined]


class LineNumberArea(QWidget):
    def __init__(self, editor: "TacxCodeEditor"):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)


class TacxCodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lineNumberArea = LineNumberArea(self)
        self.setTabStopDistance(_font_advance(self, "    "))
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self._highlight_current_line)
        self.updateLineNumberAreaWidth(0)
        self._highlight_current_line()

    def lineNumberAreaWidth(self) -> int:
        digits = 1
        maximum = max(1, self.blockCount())
        while maximum >= 10:
            maximum //= 10
            digits += 1
        return 12 + _font_advance(self, "9") * digits

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor("#1d1f23"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#8a8f98"))
                painter.drawText(0, top, self.lineNumberArea.width() - 6, self.fontMetrics().height(), ALIGN_RIGHT, number)
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def _highlight_current_line(self):
        selection = QTextEdit.ExtraSelection()
        line_color = QColor("#253448")
        selection.format.setBackground(line_color)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

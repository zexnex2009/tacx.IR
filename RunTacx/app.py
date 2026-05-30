from __future__ import annotations

from pathlib import Path

try:
    from PyQt6.QtCore import QSettings, Qt
    from PyQt6.QtGui import QAction, QKeySequence
    from PyQt6.QtWidgets import (
        QApplication,
        QDockWidget,
        QFileDialog,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
    APP_EXEC_ATTR = "exec"
    QT_APP_EXEC_ATTR = APP_EXEC_ATTR
    HORIZONTAL = Qt.Orientation.Horizontal
    LEFT_DOCK = Qt.DockWidgetArea.LeftDockWidgetArea
    RIGHT_DOCK = Qt.DockWidgetArea.RightDockWidgetArea
    USER_ROLE = Qt.ItemDataRole.UserRole
except ImportError:  # pragma: no cover - exercised only when PyQt6 is unavailable
    from PyQt5.QtCore import QSettings, Qt
    from PyQt5.QtGui import QAction, QKeySequence
    from PyQt5.QtWidgets import (
        QApplication,
        QDockWidget,
        QFileDialog,
        QHBoxLayout,
        QInputDialog,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
    APP_EXEC_ATTR = "exec_"
    QT_APP_EXEC_ATTR = APP_EXEC_ATTR
    HORIZONTAL = Qt.Horizontal
    LEFT_DOCK = Qt.LeftDockWidgetArea
    RIGHT_DOCK = Qt.RightDockWidgetArea
    USER_ROLE = Qt.UserRole

from .editor import TacxCodeEditor
from .highlighter import TacxSyntaxHighlighter
from .project import MAX_RECENT_FILES, discover_example_files, normalize_recent_files
from .runner import RunResult, load_source, run_source

RECENT_FILES_KEY = "recentFiles"
GEOMETRY_KEY = "geometry"
WINDOW_STATE_KEY = "windowState"


def _standard_key_sequence(name: str) -> QKeySequence:
    standard_key = getattr(QKeySequence, "StandardKey", None)
    if standard_key is not None:
        return QKeySequence(getattr(standard_key, name))
    return QKeySequence(getattr(QKeySequence, name))


class TacxWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings()
        self.current_path: Path | None = None
        self.current_display_name = "Untitled"
        self._build_ui()
        self._restore_settings()
        self._refresh_examples()
        self._refresh_recent_files()
        self._update_title()
        self._update_cursor_status()

    def _build_ui(self):
        self.setWindowTitle("RunTacx")
        self.resize(1200, 820)

        self.editor = TacxCodeEditor(self)
        self.editor.setPlaceholderText("Open a .tacx file or paste Tacx.IR code here.")
        self.highlighter = TacxSyntaxHighlighter(self.editor.document())
        self.editor.cursorPositionChanged.connect(self._update_cursor_status)
        self.editor.textChanged.connect(self._update_title)

        self.output = QPlainTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Program output and errors appear here.")

        splitter = QSplitter(HORIZONTAL, self)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.output)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        root = QWidget(self)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        toolbar_row = QHBoxLayout()
        self.path_label = QLabel("No file loaded")
        self.path_label.setWordWrap(True)

        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(_standard_key_sequence("Open"))
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(_standard_key_sequence("Save"))
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setShortcut(_standard_key_sequence("SaveAs"))
        self.save_as_action.triggered.connect(self.save_file_as)

        self.run_action = QAction("Run", self)
        self.run_action.setShortcut(QKeySequence("F5"))
        self.run_action.triggered.connect(self.run_current_file)

        self.clear_action = QAction("Clear Output", self)
        self.clear_action.setShortcut(QKeySequence("Ctrl+L"))
        self.clear_action.triggered.connect(self.clear_output)

        for action in (self.open_action, self.save_action, self.save_as_action, self.run_action, self.clear_action):
            self.addAction(action)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.open_file)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_file)
        save_as_btn = QPushButton("Save As")
        save_as_btn.clicked.connect(self.save_file_as)
        run_btn = QPushButton("Run")
        run_btn.clicked.connect(self.run_current_file)
        clear_btn = QPushButton("Clear Output")
        clear_btn.clicked.connect(self.clear_output)

        toolbar_row.addWidget(self.path_label, 1)
        toolbar_row.addWidget(open_btn)
        toolbar_row.addWidget(save_btn)
        toolbar_row.addWidget(save_as_btn)
        toolbar_row.addWidget(run_btn)
        toolbar_row.addWidget(clear_btn)

        layout.addLayout(toolbar_row)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(root)

        self.cursor_label = QLabel("Ln 1, Col 1")
        self.statusBar().addPermanentWidget(self.cursor_label)
        self.statusBar().showMessage("Ready")

        self._build_navigation_dock()

    def _build_navigation_dock(self):
        dock = QDockWidget("Library", self)
        dock.setAllowedAreas(LEFT_DOCK | RIGHT_DOCK)

        tabs = QTabWidget(dock)
        self.recent_list = QListWidget(tabs)
        self.examples_list = QListWidget(tabs)
        self.recent_list.itemActivated.connect(self._open_item_from_list)
        self.examples_list.itemActivated.connect(self._open_item_from_list)
        tabs.addTab(self.recent_list, "Recent")
        tabs.addTab(self.examples_list, "Examples")
        dock.setWidget(tabs)
        self.addDockWidget(LEFT_DOCK, dock)

    def _restore_settings(self):
        geometry = self.settings.value(GEOMETRY_KEY)
        if geometry:
            self.restoreGeometry(geometry)
        state = self.settings.value(WINDOW_STATE_KEY)
        if state:
            self.restoreState(state)

    def _save_settings(self):
        self.settings.setValue(GEOMETRY_KEY, self.saveGeometry())
        self.settings.setValue(WINDOW_STATE_KEY, self.saveState())
        self.settings.setValue(RECENT_FILES_KEY, self._recent_files())

    def _settings_recent_files(self) -> list[str]:
        raw = self.settings.value(RECENT_FILES_KEY, [])
        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw]
        if isinstance(raw, tuple):
            return [str(item) for item in raw]
        return [str(item) for item in raw]

    def _recent_files(self) -> list[str]:
        current = []
        if self.current_path is not None and self.current_path.exists():
            current.append(str(self.current_path.resolve()))
        current.extend(self._settings_recent_files())
        return normalize_recent_files(current, limit=MAX_RECENT_FILES)

    def _set_recent_files(self, files: list[str]):
        self.settings.setValue(RECENT_FILES_KEY, files)
        self._refresh_recent_files()

    def _push_recent_file(self, path: Path):
        recent = [str(path.resolve())]
        recent.extend(self._settings_recent_files())
        self._set_recent_files(normalize_recent_files(recent, limit=MAX_RECENT_FILES))

    def _display_name(self, path: Path) -> str:
        return path.name if path.name else str(path)

    def _refresh_examples(self):
        self.examples_list.clear()
        for path in discover_example_files():
            item = QListWidgetItem(self._display_name(path))
            item.setToolTip(str(path))
            item.setData(USER_ROLE, str(path))
            self.examples_list.addItem(item)

    def _refresh_recent_files(self):
        self.recent_list.clear()
        for entry in self._recent_files():
            path = Path(entry)
            if not path.exists():
                continue
            item = QListWidgetItem(self._display_name(path))
            item.setToolTip(str(path))
            item.setData(USER_ROLE, str(path))
            self.recent_list.addItem(item)

    def _open_item_from_list(self, item: QListWidgetItem):
        path = Path(item.data(USER_ROLE))
        self.load_file(path)

    def _update_title(self):
        suffix = "*" if self.editor.document().isModified() else ""
        self.setWindowTitle(f"RunTacx - {self.current_display_name}{suffix}")

    def _update_cursor_status(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.positionInBlock() + 1
        self.cursor_label.setText(f"Ln {line}, Col {column}")

    def append_output(self, text: str):
        if text:
            self.output.appendPlainText(text.rstrip("\n"))

    def clear_output(self):
        self.output.clear()
        self.statusBar().showMessage("Output cleared", 2000)

    def load_file(self, path: Path):
        try:
            source = load_source(path)
        except OSError as exc:
            QMessageBox.critical(self, "Open failed", str(exc))
            return

        self.editor.setPlainText(source)
        self.editor.document().setModified(False)
        self.current_path = path
        self.current_display_name = self._display_name(path)
        self.path_label.setText(str(path))
        self._push_recent_file(path)
        self._update_title()
        self._update_cursor_status()
        self.statusBar().showMessage(f"Loaded {path.name}", 2500)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Tacx.IR file",
            str(self.current_path.parent if self.current_path else Path.cwd()),
            "Tacx.IR files (*.tacx);;All files (*)",
        )
        if filename:
            self.load_file(Path(filename))

    def _write_file(self, path: Path):
        path.write_text(self.editor.toPlainText(), encoding="utf-8")
        self.current_path = path
        self.current_display_name = self._display_name(path)
        self.path_label.setText(str(path))
        self.editor.document().setModified(False)
        self._push_recent_file(path)
        self._update_title()
        self.statusBar().showMessage(f"Saved {path.name}", 2500)

    def save_file(self):
        if self.current_path is None:
            self.save_file_as()
            return
        try:
            self._write_file(self.current_path)
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Tacx.IR file",
            str(self.current_path if self.current_path else Path.cwd() / "untitled.tacx"),
            "Tacx.IR files (*.tacx);;All files (*)",
        )
        if not filename:
            return
        try:
            self._write_file(Path(filename))
        except OSError as exc:
            QMessageBox.critical(self, "Save failed", str(exc))

    def _input_provider(self):
        def provider() -> str:
            text, ok = QInputDialog.getText(self, "Tacx.IR Input", "Enter value for poro:")
            if not ok:
                raise RuntimeError("Input cancelled by user")
            return text

        return provider

    def _handle_run_result(self, result: RunResult):
        if result.output:
            self.append_output(result.output)
        if result.ok:
            self.statusBar().showMessage("Program completed successfully", 2500)
            return
        if result.error:
            self.append_output(result.error)
            QMessageBox.warning(self, "Tacx.IR error", result.error)
        self.statusBar().showMessage("Program failed", 2500)

    def run_source(self, source: str):
        result = run_source(source, input_provider=self._input_provider())
        self._handle_run_result(result)

    def run_current_file(self):
        source = self.editor.toPlainText()
        if not source.strip():
            QMessageBox.information(self, "RunTacx", "The editor is empty.")
            return
        self.run_source(source)

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)


def create_application() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

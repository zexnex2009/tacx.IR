# RunTacx

RunTacx is a small native desktop launcher for Tacx.IR `.tacx` files. It is built with PyQt and reuses the repository's existing `tacxir` interpreter package, so it does not duplicate the language runtime.

## What it does

- Open, edit, and save `.tacx` files
- Run the current buffer inside the app
- Show program output in a dedicated output pane
- Prompt for `poro` input with a modal dialog
- Highlight Tacx.IR syntax in the editor
- Show line numbers in the editor
- Show the current cursor position in the status bar
- Keep a recent files list
- Show an examples browser with the bundled sample programs

## What is included

- [`main.py`](main.py): the application entry point
- [`app.py`](app.py): the main window and UI wiring
- [`editor.py`](editor.py): code editor with line numbers
- [`highlighter.py`](highlighter.py): syntax highlighting rules
- [`runner.py`](runner.py): source execution helper
- [`project.py`](project.py): example discovery and recent-file helpers
- [`RunTacx.bat`](RunTacx.bat): Windows double-click launcher
- [`examples/`](examples): bundled sample programs
- [`tests/`](tests): smoke tests for the non-GUI pieces

## Requirements

- Python 3.10 or newer
- PyQt5 5.15+ installed in the Python environment

The code is also compatible with PyQt6, but the default dependency list installs PyQt5.

Install the dependency:

```powershell
python -m pip install -r RunTacx/requirements.txt
```

## How to run

From the repository root:

```powershell
python RunTacx/main.py
```

You can also run it through the installed entry point after packaging:

```powershell
runtacx
```

On Windows, double-click [`RunTacx.bat`](RunTacx.bat) to launch the app.

## Recent files

RunTacx remembers recent files using Qt settings under the current application identity. The list is refreshed when you open or save a file. Missing files are automatically skipped.

## Examples browser

The Examples tab scans [`examples/`](examples) for `*.tacx` files and lets you open them with one click. The current repository ships with [`examples/hello.tacx`](examples/hello.tacx).

## Behavior notes

- The editor runs the current buffer directly, so you can test unsaved changes.
- Output from `bolo` is captured into the lower pane.
- If the program calls `poro`, RunTacx shows an input dialog.
- Runtime and syntax errors are surfaced in the UI and also shown in the output pane.
- File paths are handled as local filesystem paths only; the app does not fetch remote sources.

## Testing

The non-GUI support code has smoke tests:

```powershell
python -m unittest -v RunTacx.tests.test_runner RunTacx.tests.test_project
```


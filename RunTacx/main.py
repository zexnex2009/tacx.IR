from __future__ import annotations

import sys
from pathlib import Path


def _add_repo_root_to_path():
    repo_root = Path(__file__).resolve().parents[1]
    root_text = str(repo_root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)


def main() -> int:
    _add_repo_root_to_path()
    from RunTacx.app import APP_EXEC_ATTR, TacxWindow, create_application

    app = create_application()
    app.setOrganizationName("TacxIR")
    app.setApplicationName("RunTacx")
    app.setApplicationDisplayName("RunTacx")
    window = TacxWindow()
    window.show()
    return getattr(app, APP_EXEC_ATTR)()


if __name__ == "__main__":
    raise SystemExit(main())

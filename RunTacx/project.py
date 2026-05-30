from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

MAX_RECENT_FILES = 10


def package_dir() -> Path:
    return Path(__file__).resolve().parent


def examples_dir() -> Path:
    return package_dir() / "examples"


def discover_example_files() -> List[Path]:
    folder = examples_dir()
    if not folder.exists():
        return []
    return sorted(
        (path for path in folder.glob("*.tacx") if path.is_file()),
        key=lambda path: path.name.casefold(),
    )


def normalize_recent_files(entries: Iterable[str], limit: int = MAX_RECENT_FILES) -> list[str]:
    recent: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        path = Path(entry).expanduser()
        if not path.exists():
            continue
        normalized = str(path.resolve())
        if normalized in seen:
            continue
        seen.add(normalized)
        recent.append(normalized)
        if len(recent) >= limit:
            break
    return recent


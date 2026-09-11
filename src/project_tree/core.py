from __future__ import annotations

import fnmatch
import os
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

# Default ignored patterns
DEFAULT_IGNORED_PATTERNS: List[str] = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".venv*",
    ".idea*",
    ".env",
    ".env.*",
    ".env-*",
    ".git",
    ".gitignore",
]

# Box-drawing characters
BRANCH = "├── "
LAST = "└── "
PIPE = "│   "
SPACE = "    "


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:           return f"{size_bytes}B"
    elif size_bytes < 1024 ** 2:    return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 ** 3:    return f"{size_bytes / (1024 ** 2):.1f}MB"
    else:                           return f"{size_bytes / (1024 ** 3):.2f}GB"


def load_excludefile(path: Optional[str]) -> List[str]:
    """Load patterns from a .gitignore-like file."""
    if not path: return []
    p = Path(path).expanduser().resolve()
    if not p.exists(): raise FileNotFoundError(f"Ignore file '{p}' does not exist")
    if not p.is_file(): raise IsADirectoryError(f"Ignore file '{p}' is not a regular file")

    patterns: List[str] = []
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"): continue
        patterns.append(line)

    return patterns


def is_ignored(name: str, relative_path: str, patterns: Sequence[str]) -> bool:
    """Return True if `name` or `relative_path` matches any ignore pattern."""
    for pattern in patterns:
        if pattern.endswith("/"):
            stripped = pattern[:-1]
            if name == stripped or fnmatch.fnmatch(name, stripped): return True
            if fnmatch.fnmatch(relative_path, stripped): return True
            continue

        if name == pattern: return True

        if fnmatch.fnmatch(name, pattern): return True

        if fnmatch.fnmatch(relative_path, pattern): return True
        if fnmatch.fnmatch(relative_path, pattern.lstrip("/")): return True

        parts = relative_path.split("/")
        if any(fnmatch.fnmatch(part, pattern) for part in parts): return True

    return False


def _safe_iterdir(path: Path) -> List[Path]:
    """Return sorted directory entries; directories first, then files."""
    try: entries = list(path.iterdir())
    except (PermissionError, OSError): return []

    entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))

    return entries


def _build_tree(path: Path, prefix: str, patterns: Sequence[str], show_size: bool, root: Path, visited: set) -> List[str]:
    lines: List[str] = []
    real = path.resolve()

    if real in visited: return [f"{prefix}[symlink cycle: {path.name}]"]
    visited.add(real)

    entries = _safe_iterdir(path)

    visible: List[Path] = []
    for entry in entries:
        try: rel = entry.relative_to(root).as_posix()
        except ValueError: rel = entry.name

        if is_ignored(entry.name, rel, patterns): continue
        visible.append(entry)

    for idx, entry in enumerate(visible):
        is_last = idx == len(visible) - 1
        connector = LAST if is_last else BRANCH
        extension = SPACE if is_last else PIPE

        try: rel = entry.relative_to(root).as_posix()
        except ValueError: rel = entry.name

        if is_ignored(entry.name, rel, patterns): continue

        if entry.is_symlink():
            target = os.readlink(entry)
            lines.append(f"{prefix}{connector}{entry.name} -> {target}")
            continue

        if entry.is_dir():
            lines.append(f"{prefix}{connector}{entry.name}/")
            lines.extend(_build_tree(entry, prefix + extension, patterns, show_size, root, visited))
        else:
            size_str = ""
            if show_size:
                try:
                    size_str = f"  ({format_size(entry.stat().st_size)})"
                except OSError:
                    size_str = "  (unknown)"
            lines.append(f"{prefix}{connector}{entry.name}{size_str}")

    visited.discard(real)

    return lines


def generate_tree(root: Path, extra_ignored: Iterable[str], show_size: bool, excludefile: Optional[str]) -> str:
    """Build the entire tree as a single string."""
    patterns: List[str] = list(DEFAULT_IGNORED_PATTERNS)
    patterns.extend(p for p in extra_ignored if p)
    patterns.extend(load_excludefile(excludefile))

    visited: set = set()
    header = f"{root.name}/"
    body = _build_tree(root, "", patterns, show_size, root, visited)

    return "\n".join([header, *body])
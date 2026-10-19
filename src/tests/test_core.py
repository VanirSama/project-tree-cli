from __future__ import annotations

from pathlib import Path

import pytest

from project_tree_cli.core import (
    DEFAULT_IGNORED_PATTERNS,
    format_size,
    is_ignored,
    generate_tree,
    load_excludefile,
)


def test_format_size():
    assert format_size(0) == "0B"
    assert format_size(512) == "512B"
    assert format_size(1024) == "1.0KB"
    assert format_size(1024 ** 2) == "1.0MB"
    assert format_size(1024 ** 3).endswith("GB")


def test_default_ignored_patterns_match_common_dirs():
    assert is_ignored("__pycache__", "__pycache__", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".venv", ".venv", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".venv-prod", ".venv-prod", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".idea", ".idea", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".env", ".env", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".env.local", ".env.local", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".env-production", ".env-production", DEFAULT_IGNORED_PATTERNS)
    assert is_ignored(".git", ".git", DEFAULT_IGNORED_PATTERNS)


def test_default_ignored_does_not_match_unrelated():
    assert not is_ignored("README.md", "README.md", DEFAULT_IGNORED_PATTERNS)
    assert not is_ignored("main.py", "src/main.py", DEFAULT_IGNORED_PATTERNS)


def test_load_gitignore(tmp_path: Path):
    g = tmp_path / ".gitignore"
    g.write_text("# comment\nnode_modules/\n*.log\n\nbuild\n", encoding="utf-8")
    patterns = load_excludefile(str(g))
    assert patterns == ["node_modules/", "*.log", "build"]


def test_generate_tree_basic(tmp_path: Path):
    (tmp_path / "a.py").write_text("print('a')")
    (tmp_path / "b").mkdir()
    (tmp_path / "b" / "c.txt").write_text("hello")
    out = generate_tree(tmp_path, [], False, None)
    assert "a.py" in out
    assert "b/" in out
    assert "c.txt" in out


def test_generate_tree_with_sizes(tmp_path: Path):
    (tmp_path / "small.txt").write_text("x" * 100)
    out = generate_tree(tmp_path, [], True, None)
    assert "100B" in out


def test_generate_tree_ignores_defaults(tmp_path: Path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "junk.pyc").write_text("")
    (tmp_path / ".venv").mkdir()
    out = generate_tree(tmp_path, [], False, None)
    assert "__pycache__" not in out
    assert ".venv" not in out


def test_generate_tree_extra_ignored(tmp_path: Path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "x.js").write_text("")
    (tmp_path / "main.py").write_text("")
    out = generate_tree(tmp_path, ["node_modules"], False, None)
    assert "node_modules" not in out
    assert "main.py" in out


def test_generate_tree_with_gitignore_file(tmp_path: Path):
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "artifact.txt").write_text("")
    (tmp_path / "main.py").write_text("")
    g = tmp_path / ".myignore"
    g.write_text("build/\n", encoding="utf-8")
    out = generate_tree(tmp_path, [], False, str(g))
    assert "build" not in out
    assert "main.py" in out
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from project_tree_cli import __version__
from project_tree_cli.core import generate_tree
from project_tree_cli.utils import print_error, print_info


def _parse_ignore_items(items: Sequence[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        for part in item.split(","):
            part = part.strip()
            if part: out.append(part)

    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="project-tree",
        description="Print a recursive tree structure of a project.",
        epilog=(
            "Examples:\n"
            "  project-tree\n"
            "  project-tree ./my-project -s\n"
            "  project-tree -i node_modules dist *.log\n"
            "  project-tree -i build,*.tmp -f\n"
            "  project-tree -g .ignore -s -f\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project directory (default: current directory).",
    )
    parser.add_argument(
        "-i", "--ignore",
        nargs="*",
        default=[],
        metavar="PATTERN",
        help="Additional file/folder patterns to ignore (space- or comma-separated).",
    )
    parser.add_argument(
        "-s", "--size",
        action="store_true",
        help="Include human-readable file sizes in the output.",
    )
    parser.add_argument(
        "-e", "--excludefile",
        default=None,
        metavar="FILE",
        help="Path to a .gitignore-like file with additional ignore patterns.",
    )
    parser.add_argument(
        "-o", "--output",
        nargs="?",
        const="project-tree.txt",
        default=None,
        metavar="FILE",
        help="Write the output to custom output file path (project-tree.txt in the project root by default).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"project-tree {__version__}",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        parser = build_parser()
        args = parser.parse_args(argv)

        root = Path(args.path).expanduser().resolve()
        if not root.exists(): raise FileNotFoundError(f"Path '{root}' does not exist.")
        if not root.is_dir(): raise NotADirectoryError(f"Path '{root}' is not a directory.")

        extra_ignored = _parse_ignore_items(args.ignore)

        output = generate_tree(
            root=root,
            extra_ignored=extra_ignored,
            show_size=args.size,
            excludefile=args.excludefile,
        )

        out_path: Optional[Path] = None
        if args.output: out_path = Path(args.output).expanduser().resolve()

        if out_path is not None:
            out_path.write_text(output + "\n", encoding="utf-8")
            print_info(f"Output written to {out_path}")
        else: print(output)

        return 0

    except KeyboardInterrupt:
        print_error("Interrupted by user.")
        return 130

    except Exception as exc:
        print_error(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
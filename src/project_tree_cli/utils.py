from __future__ import annotations

import sys
from typing import TextIO

RED     = "\033[0;91m"
GREEN   = "\033[0;92m"
YELLOW  = "\033[0;93m"
RESET   = "\033[0m"


def supports_color(stream: TextIO) -> bool: return True if sys.stdout.isatty() else False

def colorize(text: str, color: str) -> str: return f"{color}{text}{RESET}"

def print_error(message: str) -> None:
    colored = colorize(message, RED) if supports_color(sys.stderr) else message
    print(colored, file=sys.stderr)

def print_info(message: str) -> None:
    colored = colorize(message, YELLOW) if supports_color(sys.stdout) else message
    print(colored, file=sys.stdout)
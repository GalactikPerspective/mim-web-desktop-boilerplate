import platform
from pathlib import Path
from typing import Iterable

import click

is_windows = platform.system() == "Windows"


class EnsurePath(Path):
    def ensure(self, with_ignore: bool = False) -> None:
        self.mkdir(parents=True, exist_ok=True)
        if with_ignore:
            with open(self / ".gitignore", "w+") as gitignore_file:
                gitignore_file.write("*")


CACHE_DIR = EnsurePath(__file__).parent / ".cache"
CACHE_DIR.ensure(with_ignore=True)


PROJECT_DIR = EnsurePath(__file__).parent.parent


# Colored prints


def log(message: str, *, bold: bool = False) -> None:
    click.echo(click.style(message, bold=bold))


def success(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="green", bold=bold))


def warning(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="yellow", bold=bold))


def error(message: str, *, bold: bool = True) -> None:
    click.echo(click.style(message, fg="red", bold=bold), err=True)


# Read / Write to files
"""
We use custom functions to read and write lines to files because some files in Element have different and / or weird
encodings, specially translation files with "weird characters".

By opening as bytes and manually encoding / decoding them, we can get around this issue.
"""


def read_lines(path: Path) -> list[str]:
    with open(path, "rb") as file:
        return [l.decode() for l in file.readlines()]


def write_lines(path: Path, lines: Iterable[str]) -> None:
    with open(path, "wb+") as file:
        file.writelines([l.encode() for l in lines])

import difflib
import filecmp
import subprocess
from pathlib import Path
from typing import Iterable

from cli.utils import read_lines


def is_file_equal(file1: Path, file2: Path) -> bool:
    return filecmp.cmp(file1, file2)


def apply_patch_file(patch_file: Path, file: Path) -> None:
    subprocess.run(
        ["patch", "-f", "-r -", "--no-backup-if-mismatch", file.as_posix(), patch_file.as_posix()],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def generate_patch(source_file: Path, original_file: Path) -> Iterable[str]:
    original_lines = read_lines(original_file)
    source_lines = read_lines(source_file)
    return list(difflib.unified_diff(source_lines, original_lines))

"""File utilities for temporary file management."""
import os
import tempfile
import shutil
from contextlib import contextmanager
from typing import Generator


@contextmanager
def TempDir(prefix: str = "musegen_") -> Generator[str, None, None]:
    """Context manager that creates a temporary directory and cleans up afterwards.

    Yields:
        Absolute path of the temporary directory.
    """
    tmp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def ensure_dir(path: str) -> str:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path.

    Returns:
        The same path.
    """
    os.makedirs(path, exist_ok=True)
    return path


def get_extension(filename: str) -> str:
    """Get the file extension without leading dot.

    Args:
        filename: Filename.

    Returns:
        Extension string (e.g. 'mp4', 'png').
    """
    return os.path.splitext(filename)[1].lstrip(".")

"""
paths.py - Project Directory Paths.

This module defines commonly used directory paths within the project,
allowing easy access to various file locations such as data, assets,
and API modules.

Constants:
    - PWD: Absolute path to the current file.
    - BASE_DIR: Root directory of the project.
    - API_DIR: Directory containing API-related modules.
    - DATA_DIR: Directory containing all project data.
    - RAW_DIR: Subdirectory for raw data storage.
    - ASSETS_DIR: Subdirectory for storing asset files.
    - TEST_DIR: Directory for unit tests.

Functions:
    - print_dirs(): Prints all key project directories for debugging.

Usage:
Import this module whenever directory paths are needed within the project.

Example:
python
    from src.utils.paths import BASE_DIR, DATA_DIR
    print(BASE_DIR)
    print(DATA_DIR)
"""

from pathlib import Path

PWD = Path(__file__).resolve()
BASE_DIR = PWD.parent.parent.parent
API_DIR = BASE_DIR / "src" / "api"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
ASSETS_DIR = DATA_DIR / "assets"
TEST_DIR = BASE_DIR / "test"


def print_dirs():
    """Print the key project directories for debugging and verification."""
    print(f"Base Directory: {BASE_DIR}")
    print(f"API Directory: {API_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Raw Directory: {RAW_DIR}")
    print(f"Assets Directory: {ASSETS_DIR}")
    print(f"Test directory: {TEST_DIR}")


if __name__ == "__main__":
    """Entry point for testing and displaying directory paths."""
    print_dirs()

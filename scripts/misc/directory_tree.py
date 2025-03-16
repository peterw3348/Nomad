"""
directory_tree.py - Project Directory Structure Utility.

Version: 0.1.0

This script generates a visual representation of the project's directory structure,
while respecting the `.gitignore` file and skipping hidden files.

Functions:
    - load_gitignore(root_dir): Reads `.gitignore` and returns a set of ignored paths.
    - list_directory_structure(root_dir, ignored_paths, indent="", script_name=None):
      Recursively prints the directory structure while ignoring `.gitignore` entries and hidden files.

Usage:
Run this script in the root directory of the project to display its structure.

Example:
python
    python directory_tree.py
"""

import os


def load_gitignore(root_dir):
    """
    Read the `.gitignore` file and returns a set of paths to ignore.

    Args:
        root_dir (str): Root directory where the `.gitignore` file is located.

    Returns:
        set: A set of ignored file and directory paths.
    """
    gitignore_path = os.path.join(root_dir, ".gitignore")
    ignored_paths = set()

    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_paths.add(os.path.normpath(line))

    return ignored_paths


def list_directory_structure(root_dir, ignored_paths, indent="", script_name=None):
    """
    Recursively prints the directory structure while ignoring `.gitignore` entries and hidden files.

    Args:
        root_dir (str): The root directory to start listing from.
        ignored_paths (set): A set of paths to ignore, typically from `.gitignore`.
        indent (str, optional): Indentation string used for formatting output. Defaults to "".
        script_name (str, optional): Name of the script to exclude from the output. Defaults to None.
    """
    try:
        entries = sorted(os.listdir(root_dir))

        for index, entry in enumerate(entries):
            entry_path = os.path.join(root_dir, entry)
            relative_entry_path = os.path.relpath(entry_path, root_dir)

            if script_name and entry == script_name:
                continue

            if any(
                relative_entry_path.startswith(ignored) for ignored in ignored_paths
            ):
                continue

            if entry.startswith("."):
                continue

            is_last = index == len(entries) - 1
            prefix = "└── " if is_last else "├── "
            print(indent + prefix + entry)

            if os.path.isdir(entry_path):
                new_indent = indent + ("    " if is_last else "│   ")
                list_directory_structure(
                    entry_path, ignored_paths, new_indent, script_name
                )

    except PermissionError:
        print(indent + "└── [Permission Denied]")


if __name__ == "__main__":
    """Entry point for generating and displaying the directory tree structure."""
    root_folder = os.getcwd()
    ignored_paths = load_gitignore(root_folder)
    script_name = os.path.basename(__file__)

    list_directory_structure(root_folder, ignored_paths, script_name=script_name)

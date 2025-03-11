# Utility script to express project structure in tree format

import os

def load_gitignore(root_dir):
    """ Reads .gitignore and returns a set of ignored paths """
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
    """ Recursively prints the directory structure while ignoring .gitignore & hidden files """
    try:
        entries = sorted(os.listdir(root_dir))

        for index, entry in enumerate(entries):
            entry_path = os.path.join(root_dir, entry)
            relative_entry_path = os.path.relpath(entry_path, root_dir)

            if script_name and entry == script_name:
                continue

            if any(relative_entry_path.startswith(ignored) for ignored in ignored_paths):
                continue

            if entry.startswith("."):
                continue

            is_last = (index == len(entries) - 1)
            prefix = "└── " if is_last else "├── "
            print(indent + prefix + entry)

            if os.path.isdir(entry_path):
                new_indent = indent + ("    " if is_last else "│   ")
                list_directory_structure(entry_path, ignored_paths, new_indent, script_name)

    except PermissionError:
        print(indent + "└── [Permission Denied]")

if __name__ == "__main__":
    root_folder = os.getcwd()
    ignored_paths = load_gitignore(root_folder)
    script_name = os.path.basename(__file__)

    list_directory_structure(root_folder, ignored_paths, script_name=script_name)

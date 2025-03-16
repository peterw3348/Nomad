"""
champion_mapping.py - Champion ID Mapping Utility.

Version: 0.1.0

This module provides functions to load and process champion ID-to-name mappings
for League of Legends champion data.

Functions:
    - load_champion_mapping(): Loads the champion ID-to-name mapping from champions.json.
    - substitute_champion_ids(data): Converts champion IDs into readable champion names.

Usage:
Import and use these functions for processing champion ID mappings.

Example:
python
    from src.utils.champion_mapping import substitute_champion_ids
    data = {'team': [136, 64, 54]}
    converted = substitute_champion_ids(data)
    print(converted)
"""

import json
from src.utils import paths


def load_champion_mapping():
    """
    Load the champion ID-to-name mapping from the data/champions.json file.

    Returns:
        dict: A dictionary mapping champion IDs (as strings) to champion names.
    """
    champions_file = paths.ASSETS_DIR / "champions.json"

    if not champions_file.exists():
        print(f"Error: {champions_file} not found.")
        return {}

    with champions_file.open("r") as f:
        return json.load(f)


def substitute_champion_ids(data):
    """
    Convert a dictionary containing lists of champion IDs into a dictionary with champion names.

    Args:
        data (dict): Dictionary with lists of integers representing champion IDs
            (e.g., {'team': [1, 2], 'bench': [3, 4]}).

    Returns:
        dict: Dictionary with substituted champion names
            (e.g., {'team': ['Aatrox', 'Ahri'], 'bench': ['Akali', 'Alistar']}).
    """
    champion_mapping = load_champion_mapping()

    if not isinstance(data, dict):
        print("Error: Input must be a dictionary with lists of champion IDs.")
        return {}

    return {
        key: [champion_mapping.get(str(champ_id), "Unknown") for champ_id in value]
        for key, value in data.items()
    }


if __name__ == "__main__":
    """
    Example execution to demonstrate champion ID substitution.
    """
    sanitized_data = {
        "team": [136, 64, 54, 875, 498],
        "bench": [203, 517, 86, 245, 141, 893],
    }
    converted = substitute_champion_ids(sanitized_data)
    print(json.dumps(converted, indent=2))

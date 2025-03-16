"""
validate_champion_keys.py - Champion Key Validation Script

Version: 0.1.0

This script verifies that the champion names in the updated champion ratings file match
the expected names from the champion mapping file.

Functions:
    - Validates that champion IDs correspond to the correct champion names.
    - Ensures data consistency between the `champions.json` and `updated_champion_ratings_with_names.json` files.

Usage:
Run this script to validate the integrity of champion names and IDs.

Example:
python
    python validate_champion_keys.py
"""

import json
from src.utils import paths


def validate_champion_keys():
    """
    Validates that champion IDs in `updated_champion_ratings_with_names.json`
    correctly match the names in `champions.json`.

    Raises:
        AssertionError: If a mismatch is found between the expected and actual names.
    """
    with open(paths.ASSETS_DIR / "champions.json", "r") as file:
        champions = json.load(file)

    with open(
        paths.ASSETS_DIR / "updated_champion_ratings_with_names.json", "r"
    ) as file:
        champion_ratings = json.load(file)

    # name_to_id = {v: k for k, v in champions.items()}

    for champ_id, data in champion_ratings.items():
        expected_name = data.get("name")
        actual_name = champions.get(champ_id)

        assert (
            actual_name == expected_name
        ), f"Mismatch for key {champ_id}: Expected {expected_name}, Found {actual_name}"

    print("All champion keys and names are correct!")


if __name__ == "__main__":
    """Entry point for running champion key validation."""
    validate_champion_keys()

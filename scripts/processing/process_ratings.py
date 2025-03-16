"""
process_champion_ratings.py - Champion Ratings Extraction and Processing.

Version: 0.1.0

This script processes raw champion rating data from a text file and converts it into structured JSON format.
The extracted data includes champion roles, ratings, attack styles, abilities, damage type, and difficulty.

Functions:
    - process_raw(): Parses raw champion rating data and converts it into a structured JSON format.

Usage:
Run this script to extract champion rating data and generate a JSON file.

Example:
python
    python process_champion_ratings.py
"""

import re
import json
from scripts.misc.champion_old import Champion
from src.utils import paths

input_file = paths.RAW_DIR / "ratings_raw.txt"
output_file = paths.ASSETS_DIR / "champion_ratings.json"


def process_raw():
    """
    Parse raw champion rating data and converts it into a structured JSON format.

    Outputs:
        - A JSON file containing all processed champion rating data.
    """
    champion_list = {}
    with open(input_file, "r", encoding="utf-8") as f:
        x = 0
        (
            name,
            primary,
            secondary,
            ratings,
            basic_attack,
            style_value,
            abilities,
            damage_type,
            difficulty,
        ) = [None] * 9

        for line in f:
            line = line.strip()
            if x == 0:  # First line: Champion Name, Roles, Ratings
                parts = line.split("\t")
                if len(parts) < 8:
                    continue

                name, primary, secondary, a, b, c, d, e = parts[:8]

                name = " ".join(dict.fromkeys(name.split()))

                ratings = (a, b, c, d, e)

                primary = (
                    primary.split(" ")[2] if len(primary.split(" ")) > 2 else "N/A"
                )
                secondary = (
                    secondary.split(" ")[2] if len(secondary.split(" ")) > 2 else "N/A"
                )

            elif x == 1:  # Second line: Basic Attacks, Style, Abilities
                match = re.search(
                    r"basic attacks (\w+) .*? (\d+) .*? abilities (\w+)", line
                )
                if match:
                    basic_attack, style_value, abilities = match.groups()
                else:
                    basic_attack, style_value, abilities = "N/A", 0, "N/A"

            elif x == 2:  # Third line: Damage Type, Difficulty
                damage_parts = line.split("\t")
                if len(damage_parts) < 2:
                    continue
                damage_type, difficulty = damage_parts[:2]

                champion_obj = Champion(
                    name,
                    primary,
                    secondary,
                    ratings,
                    basic_attack,
                    style_value,
                    abilities,
                    damage_type,
                    difficulty,
                )
                champion_list[name] = champion_obj.to_dict()

                print(
                    f"Champion: {name}, Primary: {primary}, Secondary: {secondary}, Ratings: {ratings}"
                )
                print(
                    f"  Basic Attacks: {basic_attack}, Style: {style_value}, Abilities: {abilities}"
                )
                print(f"  Damage Type: {damage_type}, Difficulty: {difficulty}")
                print("-" * 50)

            x = (x + 1) % 3

    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(champion_list, json_file, indent=4)

    print(f"\nProcessed {len(champion_list)} champions and saved to {output_file}.")


if __name__ == "__main__":
    """Entry point for processing champion rating data."""
    process_raw()

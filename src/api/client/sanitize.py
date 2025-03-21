"""
sanitize.py - Champion Data Extractor and Processor.

This module processes champion selection data from the League of Legends client,
extracting and grouping champion IDs for further analysis.

Functions:
    - extract_champion_ids(data): Extracts champion IDs from the lobby data.
    - group_champion_ids(data, player_puuid): Groups champion IDs into team, bench, and player categories.
    - sanitize_champion_data(data, player_puuid): Extracts and groups champion data for processing.
"""

import json
from src.utils import paths
from src.utils import converter


def extract_champion_ids(data):
    """
    Extract champion IDs from lobby data.

    Args:
        data (dict): The raw lobby data containing champion selections.

    Returns:
        dict: A dictionary containing extracted champion IDs categorized under 'benchChampions' and 'myTeam'.
    """
    keys_to_check = ["benchChampions", "myTeam"]
    extracted = {}

    for key in keys_to_check:
        if key in data:
            extracted[key] = [
                {
                    "championId": champ["championId"],
                    "puuid": champ.get("puuid", ""),
                }
                for champ in data[key]
                if champ.get("championId")
            ]

    return extracted


def group_champion_ids(data, player_puuid):
    """
    Group champion IDs based on team assignment.

    Args:
        data (dict): Dictionary containing extracted champion IDs.
        player_puuid (str): The PUUID of the current player.

    Returns:
        dict: A dictionary containing grouped champion IDs under 'team', 'bench', and 'player'.
    """
    grouped = {"team": [], "bench": [], "player": []}

    if "myTeam" in data:
        for champ in data["myTeam"]:
            if champ.get("championId"):
                if champ.get("puuid") == player_puuid:
                    grouped["player"].append(champ["championId"])
                grouped["team"].append(champ["championId"])

    if "benchChampions" in data:
        grouped["bench"] = [
            champ["championId"]
            for champ in data["benchChampions"]
            if champ.get("championId")
        ]

    return grouped


def sanitize_champion_data(data, player_puuid):
    """
    Extract and groups champion data for further processing.

    Args:
        data (dict): The raw lobby data containing champion selections.
        player_puuid (str): The PUUID of the current player.

    Returns:
        dict: A dictionary containing grouped champion IDs ready for processing.
    """
    extracted = extract_champion_ids(data)
    grouped = group_champion_ids(extracted, player_puuid)
    return grouped


if __name__ == "__main__":
    """
    Entry point for processing champion selection data.

    Reads raw champion selection data from a JSON file, processes it,
    and writes the cleaned data back to a JSON file.
    """
    input_file = paths.TEST_DIR / "lobby" / "lobby.json"
    output_file = paths.TEST_DIR / "lobby" / "lobby_clean.json"

    if not input_file.exists():
        print(f"Error: {input_file} not found.")
    else:
        with input_file.open("r") as f:
            data = json.load(f)

        player_puuid = "15c66f9d-0464-513f-a881-a72d40386dbd"
        sanitized_data = sanitize_champion_data(data, player_puuid)

        with output_file.open("w") as f:
            json.dump(sanitized_data, f, indent=2)

        sanitized_data = converter.substitute_champion_ids(sanitized_data)
        print(sanitized_data)

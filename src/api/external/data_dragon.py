"""
data_dragon.py - League of Legends Data Dragon API Fetcher.

Version: 0.1.0

This module retrieves champion data from Riot Games' Data Dragon API.
It fetches champion names and their corresponding IDs, saving the data locally.

Functions:
    - get_champion_names(): Fetches champion names and IDs from the Data Dragon API.
"""

import requests
import json
import os

from src.utils import paths

CHAMPION_URL = "https://ddragon.leagueoflegends.com/cdn/15.4.1/data/en_US/champion.json"


def get_champion_names():
    """
    Fetch champion names and their corresponding IDs from the Data Dragon API.

    Returns:
        dict: A dictionary mapping champion IDs to champion names.
        If the request fails, returns an empty dictionary.
    """
    response = requests.get(CHAMPION_URL)
    if response.status_code == 200:
        data = response.json()
        champions = {}
        for champ in data["data"]:
            champions[data["data"][champ]["key"]] = champ
        return champions
    else:
        print("Failed to fetch champion data:", response.status_code)
        return {}


if __name__ == "__main__":
    """
    Entry point for fetching champion data from Data Dragon.

    Saves champion names and IDs into a local JSON file.
    """
    champions = get_champion_names()
    file_path = os.path.join(paths.ASSETS_DIR, "champions.json")
    with open(file_path, "w") as f:
        json.dump(champions, f, indent=4)
    print("Champion data saved to data/static/champions.json")

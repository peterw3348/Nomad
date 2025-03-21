"""
data_dragon.py - Champion Name and ID Fetcher from Riot's Data Dragon API.

This module fetches a mapping of champion IDs to champion names using the
official Riot Data Dragon endpoint. It is primarily used to populate local
static data for use in ARAM analysis and overlay tools.

Functions:
    - get_champion_names(): Fetch champion names and their numeric IDs from
    the Data Dragon API.

Executed as a script, it saves the fetched data as a JSON file to the local
assets directory.
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
        If the request fails or returns invalid data, returns an empty dictionary.
    """
    response = requests.get(CHAMPION_URL)
    if response.status_code == 200:
        try:
            data = response.json()
            if "data" not in data:
                print("Malformed response: Missing 'data' key.")
                return {}

            champions = {}
            for champ in data["data"]:
                champions[data["data"][champ]["key"]] = champ
            return champions
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing Data Dragon response: {e}")
            return {}

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

import requests
import json
import os

from src.api import paths

CHAMPION_URL = "https://ddragon.leagueoflegends.com/cdn/15.4.1/data/en_US/champion.json"

def get_champion_names():
    response = requests.get(CHAMPION_URL)
    if response.status_code == 200:
        data = response.json()
        champions = {}
        for champ in data["data"]:
            champions[int(data["data"][champ]["key"])] = champ
        return champions
    else:
        print("Failed to fetch champion data:", response.status_code)
        return []

if __name__ == "__main__":
    champions = get_champion_names()
    file_name = "champions.json"
    file_path = os.path.join(paths.DATA_DIR, file_name)
    with open(file_path, "w") as f:
        json.dump(champions, f, indent=4)
    print("Champion data saved to data/champions.json")

import json
from src.utils import paths

with open("champions.json", "r") as file:
    champions = json.load(file)

with open("updated_champion_ratings_with_names.json", "r") as file:
    champion_ratings = json.load(file)

name_to_id = {v: k for k, v in champions.items()}

for champ_id, data in champion_ratings.items():
    expected_name = data.get("name")
    actual_name = champions.get(champ_id)

    assert actual_name == expected_name, f"Mismatch for key {champ_id}: Expected {expected_name}, Found {actual_name}"

print("All champion keys and names are correct!")

import json
from src.api import paths
from src.api import converter

def extract_champion_ids(data):
    keys_to_check = ["benchChampions", "myTeam"]
    extracted = {}

    for key in keys_to_check:
        if key in data:
            extracted[key] = [{"championId": champ["championId"]} for champ in data[key] if champ.get("championId")]

    return extracted

def group_champion_ids(data):
    grouped = {"team": [], "bench": []}

    if "myTeam" in data:
        grouped["team"] = [champ["championId"] for champ in data["myTeam"] if champ.get("championId")]
    if "benchChampions" in data:
        grouped["bench"] = [champ["championId"] for champ in data["benchChampions"] if champ.get("championId")]

    return grouped

def sanitize_champion_data(data):
    extracted = extract_champion_ids(data)
    grouped = group_champion_ids(extracted)
    return grouped

if __name__ == "__main__":
    input_file = paths.DATA_DIR / "test_lobby" / "lobby.json"
    output_file = paths.DATA_DIR / "test_lobby" / "lobby_clean.json"

    if not input_file.exists():
        print(f"Error: {input_file} not found.")
    else:
        with input_file.open("r") as f:
            data = json.load(f)

        sanitized_data = sanitize_champion_data(data)

        with output_file.open("w") as f:
            json.dump(sanitized_data, f, indent=2)

        sanitized_data = converter.substitute_champion_ids(sanitized_data)
        print(sanitized_data)

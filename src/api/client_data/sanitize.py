import json
from src.utils import paths
from src.utils import converter

def extract_champion_ids(data):
    keys_to_check = ["benchChampions", "myTeam"]
    extracted = {}

    for key in keys_to_check:
        if key in data:
            extracted[key] = [{"championId": champ["championId"], "puuid": champ.get("puuid", "")} for champ in data[key] if champ.get("championId")]

    return extracted

def group_champion_ids(data, player_puuid):
    grouped = {"team": [], "bench": [], "player": []}

    if "myTeam" in data:
        for champ in data["myTeam"]:
            if champ.get("championId"):
                if champ.get("puuid") == player_puuid:
                    grouped["player"].append(champ["championId"])
                grouped["team"].append(champ["championId"])

    if "benchChampions" in data:
        grouped["bench"] = [champ["championId"] for champ in data["benchChampions"] if champ.get("championId")]

    return grouped

def sanitize_champion_data(data, player_puuid):
    extracted = extract_champion_ids(data)
    grouped = group_champion_ids(extracted, player_puuid)
    return grouped

if __name__ == "__main__":
    input_file = paths.BASE_DIR / "test" / "lobby" / "lobby.json"
    output_file = paths.BASE_DIR / "test" / "lobby" / "lobby_clean.json"

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

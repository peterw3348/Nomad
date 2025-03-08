import re
import json
from scripts.champion_old import Champion
from src.utils import paths

input_file = paths.RAW_DIR / "ratings_raw.txt"
output_file = paths.STATIC_DIR / "champion_ratings.json"

def process_raw():
    champion_list = {}
    with open(input_file, "r", encoding="utf-8") as f:
        x = 0
        name, primary, secondary, ratings, basic_attack, style_value, abilities, damage_type, difficulty = [None] * 9

        for line in f:
            line = line.strip()
            if x == 0:  # First line: Champion Name, Roles, Ratings
                parts = line.split("\t")
                if len(parts) < 8:
                    continue

                name, primary, secondary, a, b, c, d, e = parts[:8]
                
                name = " ".join(dict.fromkeys(name.split()))

                ratings = (a, b, c, d, e)

                primary = primary.split(" ")[2] if len(primary.split(" ")) > 2 else "N/A"
                secondary = secondary.split(" ")[2] if len(secondary.split(" ")) > 2 else "N/A"

            elif x == 1:  # Second line: Basic Attacks, Style, Abilities
                match = re.search(r"basic attacks (\w+) .*? (\d+) .*? abilities (\w+)", line)
                if match:
                    basic_attack, style_value, abilities = match.groups()
                else:
                    basic_attack, style_value, abilities = "N/A", 0, "N/A"

            elif x == 2:  # Third line: Damage Type, Difficulty
                damage_parts = line.split("\t")
                if len(damage_parts) < 2:
                    continue
                damage_type, difficulty = damage_parts[:2]

                champion_obj = Champion(name, primary, secondary, ratings, basic_attack, style_value, abilities, damage_type, difficulty)
                champion_list[name] = champion_obj.to_dict()

                print(f"Champion: {name}, Primary: {primary}, Secondary: {secondary}, Ratings: {ratings}")
                print(f"  Basic Attacks: {basic_attack}, Style: {style_value}, Abilities: {abilities}")
                print(f"  Damage Type: {damage_type}, Difficulty: {difficulty}")
                print("-" * 50)

            x = (x + 1) % 3

    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(champion_list, json_file, indent=4)

    print(f"\nProcessed {len(champion_list)} champions and saved to {output_file}.")

if __name__ == "__main__":
    process_raw()

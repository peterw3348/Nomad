import json

def load_champion_data():
    try:
        with open("../../data/champions.json", "r") as f:
            champions = json.load(f)
        return champions
    except FileNotFoundError:
        print("Champion data file not found! Run riot_api.py first.")
        return []

if __name__ == "__main__":
    champions = load_champion_data()
    print("Loaded champions:", champions)

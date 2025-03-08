import json
from src.utils import paths

def load_champion_mapping():
    """
    Loads the champion ID-to-name mapping from data/champions.json.
    """
    champions_file = paths.STATIC_DIR / "champions.json"
    
    if not champions_file.exists():
        print(f"Error: {champions_file} not found.")
        return {}

    with champions_file.open("r") as f:
        return json.load(f)

def substitute_champion_ids(data):
    """
    Converts a dictionary containing lists of champion IDs into a dictionary with names.

    Args:
        data (dict): Dictionary with lists of integers as values (e.g., {'team': [1, 2], 'bench': [3, 4]}).

    Returns:
        dict: Dictionary with substituted champion names (e.g., {'team': ['Aatrox', 'Ahri'], 'bench': ['Akali', 'Alistar']}).
    """
    champion_mapping = load_champion_mapping()

    if not isinstance(data, dict):
        print("Error: Input must be a dictionary with lists of champion IDs.")
        return {}

    return {
        key: [champion_mapping.get(str(champ_id), "Unknown") for champ_id in value]
        for key, value in data.items()
    }

if __name__ == "__main__":
    sanitized_data = {'team': [136, 64, 54, 875, 498], 'bench': [203, 517, 86, 245, 141, 893]}
    converted = substitute_champion_ids(sanitized_data)
    print(json.dumps(converted, indent=2))

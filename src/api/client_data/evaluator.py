import json
import numpy as np
from src.utils import paths
from src.api.client_data.champion import Champ

weights = paths.STATIC_DIR / "classes" / "role_weights.json"
wr = paths.STATIC_DIR / "dd_wr.csv"

role_weights = {}
with open(weights, "r", encoding="utf-8") as file:
    role_weights = json.load(file)

role_weight_sum_tolerance = 0.5

def check_role_weight_sums():
    for role, weights in role_weights.items():
        total_weight = sum(weights.values())
        if not (5 - role_weight_sum_tolerance <= total_weight <= 5 + role_weight_sum_tolerance):
            raise ValueError(f"Role weights for {role} do not sum to 5 within tolerance {role_weight_sum_tolerance}. Current sum: {total_weight}")

check_role_weight_sums()

def diminishing_returns(x):
    return 5 + (10 * (1 - np.exp(-(x - 5) / 4)))

def apply_role_weights(champ, category):
    primary_weight = role_weights.get(champ.primary, {}).get(category, 1.0)
    secondary_weight = role_weights.get(champ.secondary, {}).get(category, 1.0)
    return champ.ratings.get(category, 0) * max(primary_weight, secondary_weight)

def fetch_win_rates():
    """Loads raw WR from file and calculates normalized WR using mean and standard deviation from the dataset."""
    win_rates = {}
    raw_wr_values = []
    
    with open(wr, "r", encoding="utf-8") as file:
        next(file)  # Skip header
        for line in file:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                _, champ_id, raw_wr = parts[:3]
                champ_id = champ_id.strip()
                raw_wr = float(raw_wr.strip().strip('%'))
                win_rates[champ_id] = raw_wr
                raw_wr_values.append(raw_wr)
    
    mean_wr = np.mean(raw_wr_values) if raw_wr_values else 50
    std_dev_wr = np.std(raw_wr_values) if raw_wr_values else 25
    
    for champ_id, raw_wr in win_rates.items():
        norm_wr = np.clip(((raw_wr - mean_wr) / std_dev_wr) * 50, -50, 50) if std_dev_wr > 0 else 0
        win_rates[champ_id] = (raw_wr, round(norm_wr, 2))
    
    return win_rates

def convert_grouped_to_champs(grouped):
    """ Converts champion IDs in grouped dict into Champ objects """
    champions = Champ.load_champs()
    win_rates = fetch_win_rates()
    
    for champ in champions.values():
        if str(champ.cid) in win_rates:
            champ.raw_wr, champ.norm_wr = win_rates[str(champ.cid)]
    
    return {
        "team": [champions[str(cid)] for cid in grouped["team"] if str(cid) in champions],
        "bench": [champions[str(cid)] for cid in grouped["bench"] if str(cid) in champions],
        "player": [champions[str(grouped["player"][0])]] if str(grouped["player"][0]) in champions else []
    }

def compute_composition_gain(grouped_champs):
    """ Computes composition gain given a dict with Champ objects """
    base_composition = {cat: 0 for cat in ["Damage", "Toughness", "Control", "Mobility", "Utility"]}
    
    for champ in grouped_champs["team"]:
        if champ.cid != grouped_champs["player"][0].cid:
            for category in base_composition:
                base_composition[category] += champ.ratings.get(category, 0)
    
    player_champ = grouped_champs["player"][0]
    player_gain = sum(
        diminishing_returns(base_composition[cat] + apply_role_weights(player_champ, cat)) -
        diminishing_returns(base_composition[cat])
        for cat in base_composition
    )
    
    gains = []
    for champ in grouped_champs["bench"]:
        comp_gain = sum(
            diminishing_returns(base_composition[cat] + apply_role_weights(champ, cat)) -
            diminishing_returns(base_composition[cat])
            for cat in base_composition
        )
        champ.raw_gain = round(comp_gain, 2)
        gains.append(comp_gain)
    
    mean_gain = np.mean(gains) if gains else 0
    std_dev_gain = np.std(gains) if gains else 1
    
    for champ in grouped_champs["bench"]:
        champ.norm_gain = np.clip(round(((champ.raw_gain - mean_gain) / std_dev_gain) * 50, 2), -50, 50) if std_dev_gain > 0 else 0
    
    player_champ.raw_gain = round(player_gain, 2)
    player_champ.norm_gain = np.clip(round(((player_gain - mean_gain) / std_dev_gain) * 50, 2), -50, 50) if std_dev_gain > 0 else 0
    
    grouped_champs["bench"].sort(key=lambda c: c.norm_gain, reverse=True)
    
    return grouped_champs

def evaluator(grouped, verbose=True):
    """ Converts champion IDs into Champ objects, computes composition gain, and returns the result """
    grouped_champs = convert_grouped_to_champs(grouped)
    result = compute_composition_gain(grouped_champs)
    
    if not verbose:
        return {
            "bench": [
                {"name": c.name, "key": c.cid, "ratings": c.ratings, "raw_gain": c.raw_gain, "raw_wr": c.raw_wr, "norm_gain": c.norm_gain, "norm_wr": c.norm_wr} 
                for c in result["bench"]
            ],
            "player": [
                {"name": c.name, "key": c.cid, "ratings": c.ratings, "raw_gain": c.raw_gain, "raw_wr": c.raw_wr, "norm_gain": c.norm_gain, "norm_wr": c.norm_wr} 
                for c in result["player"]
            ]
        }
    return result

if __name__ == "__main__":
    test_grouped = {
        "team": [136, 64, 54, 875, 498],
        "bench": [203, 517, 86, 245, 141, 893],
        "player": [498]
    }
    result = evaluator(test_grouped, verbose=False)
    print(json.dumps(result, indent=4, default=lambda o: o.__dict__))

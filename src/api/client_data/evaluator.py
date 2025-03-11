# evaluator.py - ARAM Champion Evaluation and Scoring
# Version: v0.1
# This script processes League of Legends ARAM champion select data,
# evaluates champion picks based on role weights and win rates,
# and computes optimal team compositions.

version = "v0.1"

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

def fetch_win_rates(verbose=False):
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
    
    if verbose:
        print(f"Win Rate Normalization -> Mean: {mean_wr:.2f}, Std Dev: {std_dev_wr:.2f}")
    
    for champ_id, raw_wr in win_rates.items():
        norm_wr = round(((raw_wr - mean_wr) / std_dev_wr) * 50, 2) if std_dev_wr > 0 else 0
        win_rates[champ_id] = (raw_wr, norm_wr)
    
    return win_rates

def convert_grouped_to_champs(grouped, verbose=False):
    champions = Champ.load_champs()
    win_rates = fetch_win_rates(verbose)
    
    for champ in champions.values():
        if str(champ.cid) in win_rates:
            champ.raw_wr, champ.norm_wr = win_rates[str(champ.cid)]
    
    return {
        "team": [champions[str(cid)] for cid in grouped["team"] if str(cid) in champions],
        "bench": [champions[str(cid)] for cid in grouped["bench"] if str(cid) in champions],
        "player": [champions[str(grouped["player"][0])]] if str(grouped["player"][0]) in champions else []
    }

def compute_composition_gain(grouped_champs, verbose=False):
    base_composition = {cat: 0 for cat in ["Damage", "Toughness", "Control", "Mobility", "Utility"]}

    # Compute base composition only using the 4 other teammates
    for champ in grouped_champs["team"]:
        if champ.cid != grouped_champs["player"][0].cid:
            for category in base_composition:
                base_composition[category] += champ.ratings.get(category, 0)

    player_champ = grouped_champs["player"][0]

    # Compute player's contribution to composition
    player_gain = sum(
        diminishing_returns(base_composition[cat] + apply_role_weights(player_champ, cat)) - 
        diminishing_returns(base_composition[cat])
        for cat in base_composition
    )

    # Compute composition gain for bench champs
    gains = []
    for champ in grouped_champs["bench"]:
        comp_gain = sum(
            diminishing_returns(base_composition[cat] + apply_role_weights(champ, cat)) - 
            diminishing_returns(base_composition[cat])
            for cat in base_composition
        )
        champ.raw_gain = comp_gain  # Keep full precision
        gains.append(comp_gain)

    # Ensure consistency in mean and std deviation calculations
    all_gains = gains + [player_gain]  # Include player gain in dataset
    mean_gain = np.mean(all_gains) if all_gains else 0
    std_dev_gain = max(np.std(all_gains), 1e-6)  # Ensure std_dev is never too small

    if verbose:
        print(f"Composition Gain Normalization -> Mean: {mean_gain:.4f}, Std Dev: {std_dev_gain:.4f}")

    # Normalize gains using the consistent mean/std values
    for champ in grouped_champs["bench"]:
        champ.norm_gain = round(((champ.raw_gain - mean_gain) / std_dev_gain) * 50, 2) if std_dev_gain > 0 else 0

    player_champ.raw_gain = player_gain  # Maintain precision
    player_champ.norm_gain = round(((player_gain - mean_gain) / std_dev_gain) * 50, 2) if std_dev_gain > 0 else 0

    # Score calculation remains the same
    for champ in grouped_champs["bench"]:
        champ.score = round((champ.norm_gain * 0.7) + (champ.norm_wr * 0.3), 2)
    player_champ.score = round((player_champ.norm_gain * 0.7) + (player_champ.norm_wr * 0.3), 2)

    grouped_champs["bench"].sort(key=lambda c: c.score, reverse=True)

    return grouped_champs

def evaluator(grouped, verbose=False):
    grouped_champs = convert_grouped_to_champs(grouped, verbose)
    result = compute_composition_gain(grouped_champs, verbose)
    
    if verbose:
        print(json.dumps(result, indent=4, default=lambda o: o.__dict__))
    return result

if __name__ == "__main__":
    test_grouped = {
        "team": [136, 64, 54, 875, 498],
        "bench": [203, 517, 86, 245, 141, 893],
        "player": [498]
    }
    result = evaluator(test_grouped, verbose=True)
    test_grouped_2 = {
        "team": [136, 64, 54, 875, 893],
        "bench": [203, 517, 86, 245, 141, 498],
        "player": [893]
    }
    result = evaluator(test_grouped_2, verbose=True)

# NOTE: norm_gain and norm_wr is now uncapped and fully based on Z-score scaling
# The following applies more to norm_gain, as raw_wr is naturally bounded by 0-100
# Previously, it was clipped to [-50, 50], but this artificially limited extreme values
# Now, high-performing champions can exceed 50, and low-performing ones can drop below -50
# 
# If issues arise:
# - Check if norm_gain values are excessively large (e.g., >150 or <-150)
# - Consider applying a soft normalization (e.g., log scaling) if outliers dominate results
# - Print min/max norm_gain values to debug extreme cases
# - Ensure the standard deviation isn't too small, which could cause extreme inflation
#
# Revisit this if score balancing feels off or if top picks seem too dominant
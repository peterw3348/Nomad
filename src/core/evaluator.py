"""
evaluator.py - ARAM Champion Evaluation and Scoring.

This module processes League of Legends ARAM champion select data,
evaluates champion picks based on role weights and win rates,
and computes optimal team compositions.

Functions:
    - check_role_weight_sums(): Ensures role weight sums adhere to predefined tolerances.
    - diminishing_returns(x): Applies a diminishing returns function for balancing champion impact.
    - apply_role_weights(champ, category): Computes a champion's weighted contribution to a category.
    - fetch_win_rates(verbose=False): Retrieves and normalizes champion win rates from data.
    - convert_grouped_to_champs(grouped, verbose=False): Maps champion IDs to champion objects with attributes.
    - compute_composition_gain(grouped_champs, verbose=False): Computes and normalizes composition gains for champions.
    - evaluator(grouped, verbose=False): Main function for evaluating team composition and champion selection.
"""

import json
import numpy as np
from src.utils import paths
from src.api.client.champion import Champ

# Load role weights and win rate data
weights = paths.ASSETS_DIR / "classes" / "role_weights.json"
wr = paths.ASSETS_DIR / "dd_wr.csv"

role_weights = {}
with open(weights, "r", encoding="utf-8") as file:
    role_weights = json.load(file)

role_weight_sum_tolerance = 0.5


def check_role_weight_sums():
    """
    Validate that each role's weight sum remains within an acceptable range.

    Raises:
        ValueError: If any role's weight sum deviates from the expected range.
    """
    for role, weights in role_weights.items():
        total_weight = sum(weights.values())
        if not (
            5 - role_weight_sum_tolerance
            <= total_weight
            <= 5 + role_weight_sum_tolerance
        ):
            raise ValueError(
                f"Role weights for {role} do not sum to 5 within tolerance {role_weight_sum_tolerance}. Current sum: {total_weight}"
            )


check_role_weight_sums()


def diminishing_returns(x):
    """
    Apply a diminishing returns function to prevent extreme values from skewing results.

    Args:
        x (float): The input value to apply diminishing returns.

    Returns:
        float: Adjusted value based on diminishing returns curve.
    """
    return 5 + (10 * (1 - np.exp(-(x - 5) / 4)))


def apply_role_weights(champ, category):
    """
    Compute a champion's weighted contribution to a specified category.

    Args:
        champ (Champ): The champion object containing role and rating data.
        category (str): The category to apply weighting to.

    Returns:
        float: Weighted contribution of the champion to the given category.
    """
    primary_weight = role_weights.get(champ.primary, {}).get(category, 1.0)
    secondary_weight = role_weights.get(champ.secondary, {}).get(category, 1.0)
    return champ.ratings.get(category, 0) * max(primary_weight, secondary_weight)


def fetch_win_rates(verbose=False):
    """
    Retrieve and normalizes champion win rates from a data source.

    Args:
        verbose (bool, optional): If True, prints normalization statistics. Defaults to False.

    Returns:
        dict: A dictionary mapping champion IDs to tuples of (raw win rate, normalized win rate).
    """
    win_rates = {}
    raw_wr_values = []

    with open(wr, "r", encoding="utf-8") as file:
        next(file)  # Skip header
        for line in file:
            parts = line.strip().split(",")
            if len(parts) >= 3:
                _, champ_id, raw_wr = parts[:3]
                champ_id = champ_id.strip()
                raw_wr = float(raw_wr.strip().strip("%"))
                win_rates[champ_id] = raw_wr
                raw_wr_values.append(raw_wr)

    mean_wr = np.mean(raw_wr_values) if raw_wr_values else 50
    std_dev_wr = np.std(raw_wr_values) if raw_wr_values else 25

    if verbose:
        print(
            f"Win Rate Normalization -> Mean: {mean_wr:.2f}, Std Dev: {std_dev_wr:.2f}"
        )

    for champ_id, raw_wr in win_rates.items():
        norm_wr = (
            round(((raw_wr - mean_wr) / std_dev_wr) * 50, 2) if std_dev_wr > 0 else 0
        )
        win_rates[champ_id] = (raw_wr, norm_wr)

    return win_rates


def convert_grouped_to_champs(grouped, verbose=False):
    """
    Map grouped champion IDs to their corresponding champion objects with attributes.

    Args:
        grouped (dict): A dictionary containing team, bench, and player champion IDs.
        verbose (bool, optional): If True, prints additional debug info. Defaults to False.

    Returns:
        dict: A structured dictionary containing mapped champions for team, bench, and player.
    """
    champions = Champ.load_champs()
    win_rates = fetch_win_rates(verbose)

    for champ in champions.values():
        if str(champ.cid) in win_rates:
            champ.raw_wr, champ.norm_wr = win_rates[str(champ.cid)]

    return {
        "team": [
            champions[str(cid)] for cid in grouped["team"] if str(cid) in champions
        ],
        "bench": [
            champions[str(cid)] for cid in grouped["bench"] if str(cid) in champions
        ],
        "player": (
            [champions[str(grouped["player"][0])]]
            if str(grouped["player"][0]) in champions
            else []
        ),
    }


def compute_composition_gain(grouped_champs, verbose=False):
    """
    Compute the composition gain for each champion by evaluating their impact on team composition.

    Args:
        grouped_champs (dict): Dictionary of grouped champions (team, bench, player).
        verbose (bool, optional): If True, prints normalization statistics. Defaults to False.

    Returns:
        dict: Updated grouped champions with computed and normalized composition gains.
    """
    base_composition = {
        cat: 0 for cat in ["Damage", "Toughness", "Control", "Mobility", "Utility"]
    }

    # Compute base composition only using the 4 other teammates
    for champ in grouped_champs["team"]:
        if champ.cid != grouped_champs["player"][0].cid:
            for category in base_composition:
                base_composition[category] += champ.ratings.get(category, 0)

    player_champ = grouped_champs["player"][0]

    # Compute player's contribution to composition
    player_gain = sum(
        diminishing_returns(
            base_composition[cat] + apply_role_weights(player_champ, cat)
        )
        - diminishing_returns(base_composition[cat])
        for cat in base_composition
    )

    # Compute composition gain for bench champs
    gains = []
    for champ in grouped_champs["bench"]:
        comp_gain = sum(
            diminishing_returns(base_composition[cat] + apply_role_weights(champ, cat))
            - diminishing_returns(base_composition[cat])
            for cat in base_composition
        )
        champ.raw_gain = comp_gain  # Keep full precision
        gains.append(comp_gain)

    # Ensure consistency in mean and std deviation calculations
    all_gains = gains + [player_gain]  # Include player gain in dataset
    mean_gain = np.mean(all_gains) if all_gains else 0
    std_dev_gain = max(np.std(all_gains), 1e-6)  # Ensure std_dev is never too small

    if verbose:
        print(
            f"Composition Gain Normalization -> Mean: {mean_gain:.4f}, Std Dev: {std_dev_gain:.4f}"
        )

    # Normalize gains using the consistent mean/std values
    for champ in grouped_champs["bench"]:
        champ.norm_gain = (
            round(((champ.raw_gain - mean_gain) / std_dev_gain) * 50, 2)
            if std_dev_gain > 0
            else 0
        )

    player_champ.raw_gain = player_gain  # Maintain precision
    player_champ.norm_gain = (
        round(((player_gain - mean_gain) / std_dev_gain) * 50, 2)
        if std_dev_gain > 0
        else 0
    )

    # Score calculation remains the same
    for champ in grouped_champs["bench"]:
        champ.score = round((champ.norm_gain * 0.7) + (champ.norm_wr * 0.3), 2)
    player_champ.score = round(
        (player_champ.norm_gain * 0.7) + (player_champ.norm_wr * 0.3), 2
    )

    grouped_champs["bench"].sort(key=lambda c: c.score, reverse=True)

    return grouped_champs


def evaluator(grouped, verbose=False):
    """
    Evaluate team composition and champion selection for ARAM mode.

    Args:
        grouped (dict): A dictionary containing grouped champion data.
        verbose (bool, optional): If True, prints evaluation details. Defaults to False.

    Returns:
        dict: Evaluation results with composition gains and champion scores.
    """
    grouped_champs = convert_grouped_to_champs(grouped, verbose)
    result = compute_composition_gain(grouped_champs, verbose)

    if verbose:
        print(json.dumps(result, indent=4, default=lambda o: o.__dict__))
    return result


if __name__ == "__main__":
    """
    Entry point for running the champion evaluation script with sample data.
    """
    test_grouped = {
        "team": [136, 64, 54, 875, 498],
        "bench": [203, 517, 86, 245, 141, 893],
        "player": [498],
    }
    result = evaluator(test_grouped, verbose=True)

    test_grouped_2 = {
        "team": [136, 64, 54, 875, 893],
        "bench": [203, 517, 86, 245, 141, 498],
        "player": [893],
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

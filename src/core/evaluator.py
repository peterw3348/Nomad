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
from src.api.client.champion import load_champions, ChampionPool

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
    primary = role_weights.get(champ.meta.primary, {}).get(category, 1.0)
    secondary = role_weights.get(champ.meta.secondary, {}).get(category, 1.0)
    return champ.meta.ratings.get(category, 0) * max(primary, secondary)


def fetch_win_rates(verbose=False):
    """
    Retrieve and normalizes champion win rates from a data source.

    Args:
        verbose (bool, optional): If True, prints normalization statistics. Defaults to False.

    Returns:
        dict: A dictionary mapping champion IDs to tuples of (raw win rate, normalized win rate).
    """
    win_rates, raw_values = {}, []
    with open(wr, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            _, cid, wr_val = line.strip().split(",")[:3]
            cid = cid.strip()
            raw = float(wr_val.strip().strip("%"))
            win_rates[cid] = raw
            raw_values.append(raw)
    mean, std = np.mean(raw_values), np.std(raw_values)
    for cid, raw in win_rates.items():
        norm = round(((raw - mean) / std) * 50, 2) if std > 0 else 0
        win_rates[cid] = (raw, norm)
    if verbose:
        print(f"WR normalization: mean={mean:.2f}, std={std:.2f}")
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
    champions = load_champions()
    winrates = fetch_win_rates(verbose)
    for champ in champions.values():
        if str(champ.cid) in winrates:
            champ.raw_wr, champ.norm_wr = winrates[str(champ.cid)]
    return ChampionPool(grouped, champions)


def compute_composition_gain(pool: ChampionPool, verbose=False):
    """
    Compute the composition gain for each champion by evaluating their impact on team composition.

    Args:
        grouped_champs (dict): Dictionary of grouped champions (team, bench, player).
        verbose (bool, optional): If True, prints normalization statistics. Defaults to False.

    Returns:
        dict: Updated grouped champions with computed and normalized composition gains.
    """
    base = {cat: 0 for cat in ["Damage", "Toughness", "Control", "Mobility", "Utility"]}
    for champ in pool.unavailable:
        for cat in base:
            base[cat] += champ.meta.ratings.get(cat, 0)

    player_gain = sum(
        diminishing_returns(base[cat] + apply_role_weights(pool.player, cat))
        - diminishing_returns(base[cat])
        for cat in base
    )

    gains = []
    for champ in pool.bench:
        gain = sum(
            diminishing_returns(base[cat] + apply_role_weights(champ, cat))
            - diminishing_returns(base[cat])
            for cat in base
        )
        champ.raw_gain = gain
        gains.append(gain)

    all_gains = gains + [player_gain]
    mean, std = np.mean(all_gains), max(np.std(all_gains), 1e-6)

    if verbose:
        print(f"Gain normalization: mean={mean:.4f}, std={std:.4f}")

    for champ in pool.bench:
        champ.norm_gain = round(((champ.raw_gain - mean) / std) * 50, 2)
        champ.score = round((champ.norm_gain * 0.7) + (champ.norm_wr * 0.3), 2)

    pool.player.raw_gain = player_gain
    pool.player.norm_gain = round(((player_gain - mean) / std) * 50, 2)
    pool.player.score = round(
        (pool.player.norm_gain * 0.7) + (pool.player.norm_wr * 0.3), 2
    )

    pool.bench.sort(key=lambda c: c.score, reverse=True)
    return pool


def evaluator(grouped, verbose=False):
    """
    Evaluate team composition and champion selection for ARAM mode.

    Args:
        grouped (dict): A dictionary containing grouped champion data.
        verbose (bool, optional): If True, prints evaluation details. Defaults to False.

    Returns:
        dict: Evaluation results with composition gains and champion scores.
    """
    pool = convert_grouped_to_champs(grouped, verbose)
    return compute_composition_gain(pool, verbose)


if __name__ == "__main__":
    """Entry point for running the champion evaluation script with sample data."""
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

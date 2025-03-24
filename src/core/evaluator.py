"""
evaluator.py - ARAM Champion Evaluation and Scoring.

This module processes League of Legends ARAM champion select data,
evaluates champion picks based on role weights and win rates,
and computes optimal team compositions using a modular, class-based design.

Functions:
    - check_role_weight_sums(): Validates that role weights per role sum to ~5 within a tolerance.
    - diminishing_returns(x): Applies diminishing returns to scale category scores non-linearly.
    - apply_role_weights(champ, category): Applies role-based weight multipliers to category values.
    - convert_grouped_to_champs(grouped): Initializes a ChampionPool from grouped champ IDs.
    - load_win_rates(filepath): Loads raw win rates from CSV into {cid: raw win rate} dictionary.
    - normalize_win_rates(raw_wr): Converts raw win rates into normalized Z-scores.
    - assign_win_rates(pool): Loads and assigns normalized win rates to each champion.
    - compute_raw_composition_gains(pool): Calculates each champion’s raw team contribution.
    - normalize_composition_gains(pool): Normalizes raw gains to Z-scores.
    - assign_comp_gains(pool): Computes and normalizes composition gains for all available champions.
    - compute_scores(pool): Computes final score using a weighted sum of composition gain and win rate.
    - evaluator(grouped): Legacy-compatible function wrapper for Evaluator.evaluate().

Classes:
    - Evaluator: Encapsulates the full evaluation pipeline and champion pool.
"""

import json
import numpy as np
from src.utils import paths
from src.api.client.champion import load_champions, ChampionPool

weights = paths.ASSETS_DIR / "classes" / "role_weights.json"
wr = paths.ASSETS_DIR / "dd_wr.csv"

role_weights = {}
with open(weights, "r", encoding="utf-8") as file:
    role_weights = json.load(file)

role_weight_sum_tolerance = 0.5
debug = False


def check_role_weight_sums():
    """
    Validate that each role's category weights sum to approximately 5.

    Raises:
        ValueError: If the sum of weights for any role falls outside the acceptable tolerance range.
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
    Apply a diminishing returns function to smooth out large category values.

    This prevents champions with extremely high ratings from disproportionately skewing team composition scores.

    Args:
        x (float): The raw category value to adjust.

    Returns:
        float: Adjusted value with diminishing returns applied.
    """
    return 5 + (10 * (1 - np.exp(-(x - 5) / 4)))


def apply_role_weights(champ, category):
    """
    Compute a weighted category value based on the champion's role alignment.

    This adjusts a champion’s rating in a category using predefined multipliers
    depending on their primary and secondary roles.

    Args:
        champ (ChampionState): Champion object containing metadata and ratings.
        category (str): One of the 5 rating categories (Damage, Toughness, etc.).

    Returns:
        float: Role-weighted contribution in the given category.
    """
    primary = role_weights.get(champ.meta.primary, {}).get(category, 1.0)
    secondary = role_weights.get(champ.meta.secondary, {}).get(category, 1.0)
    return champ.meta.ratings.get(category, 0) * max(primary, secondary)


def convert_grouped_to_champs(grouped):
    """
    Convert raw grouped champion ID data into a structured ChampionPool object.

    This initializes the champion pool using loaded champion metadata and
    categorizes them into team, bench, and player selections.

    Args:
        grouped (dict): Dictionary containing 'team', 'bench', and 'player' champion IDs.

    Returns:
        ChampionPool: Object encapsulating grouped and categorized champions.
    """
    champions = load_champions()
    return ChampionPool(grouped, champions)


def load_win_rates(filepath) -> dict[str, float]:
    """
    Load raw ARAM win rates from a CSV file.

    The function reads a CSV containing champion IDs and their win rates
    and returns a dictionary mapping each champion ID (as a string) to
    its win rate as a float (0-100 scale).

    The CSV is expected to have the format:
        <name>,<champion_id>,<win_rate>...

    Args:
        filepath (str or Path): Path to the CSV file containing win rate data.

    Returns:
        dict[str, float]: A mapping of champion IDs to raw win rate percentages.
    """
    raw_wr = {}
    with open(filepath, "r", encoding="utf-8") as f:
        next(f)
        for line in f:
            _, cid, wr_val = line.strip().split(",")[:3]
            raw_wr[cid.strip()] = float(wr_val.strip().strip("%"))
    return raw_wr


def normalize_win_rates(raw_wr: dict[str, float]) -> dict[str, tuple[float, float]]:
    """
    Normalize raw win rates using Z-score scaling.

    This function transforms raw win rate percentages into a normalized
    Z-score-based scale (multiplied by 50), allowing fair comparison of
    win rates independent of average performance.

    The resulting value is centered around 0 with positive values indicating
    above-average champions and negative values indicating below-average ones.

    Args:
        raw_wr (dict[str, float]): Dictionary of champion IDs to raw win rates (0-100%).

    Returns:
        dict[str, tuple[float, float]]: Dictionary mapping champion IDs to a tuple of:
            - raw win rate (float)
            - normalized win rate (float, Z-score * 50)
    """
    raw_values = list(raw_wr.values())
    mean, std = np.mean(raw_values), np.std(raw_values)
    return {
        cid: (
            raw,
            round(((raw - mean) / std) * 50, 2) if std > 0 else 0,
        )
        for cid, raw in raw_wr.items()
    }


def assign_win_rates(pool: ChampionPool):
    """
    Load and assign raw and normalized win rates to each champion in the pool.

    Applies both raw percentages and Z-score scaled values (×50) to all champions
    in `available` and `unavailable`. Champions missing from the data are skipped.

    Args:
        pool (ChampionPool): Champion pool to update with win rate data.
    """
    raw_wr = load_win_rates(wr)
    norm_wr = normalize_win_rates(raw_wr)
    if debug:
        print("WR normalization stats:", norm_wr)
    for champ in pool.available + pool.unavailable:
        cid = str(champ.cid)
        if cid in norm_wr:
            champ.raw_wr, champ.norm_wr = norm_wr[cid]


def compute_raw_composition_gains(pool: ChampionPool):
    """
    Compute how much each available champion would improve the current team composition.

    The function calculates a "raw gain" for each champion by assessing their
    contribution across all 5 categories using role weighting and diminishing returns.

    Args:
        pool (ChampionPool): The pool containing available and unavailable champions.
    """
    base = {cat: 0 for cat in ["Damage", "Toughness", "Control", "Mobility", "Utility"]}
    for champ in pool.unavailable:
        for cat in base:
            base[cat] += champ.meta.ratings.get(cat, 0)

    for champ in pool.available:
        gain = sum(
            diminishing_returns(base[cat] + apply_role_weights(champ, cat))
            - diminishing_returns(base[cat])
            for cat in base
        )
        champ.raw_gain = gain


def normalize_composition_gains(pool: ChampionPool):
    """
    Normalize raw composition gains into Z-scores to produce `norm_gain`.

    This ensures fair comparison between champions, especially when some
    raw gain values are significantly higher or lower than others.

    Args:
        pool (ChampionPool): The champion pool with raw gain values populated.
    """
    gains = [champ.raw_gain for champ in pool.available]
    mean, std = np.mean(gains), max(np.std(gains), 1e-6)
    if debug:
        print(f"Gain normalization: mean={mean:.4f}, std={std:.4f}")
    for champ in pool.available:
        champ.norm_gain = round(((champ.raw_gain - mean) / std) * 50, 2)


def assign_comp_gains(pool: ChampionPool):
    """
    Compute and normalize composition gains for all available champions.

    Combines raw gain calculation and Z-score normalization into a single step.

    Args:
        pool (ChampionPool): Champion pool to update with composition gain data.
    """
    compute_raw_composition_gains(pool)
    normalize_composition_gains(pool)


def compute_scores(pool: ChampionPool):
    """
    Compute the final score for each available champion.

    The score is a weighted blend of normalized composition gain (70%)
    and normalized win rate (30%). This value determines champion ranking
    within the bench.

    Args:
        pool (ChampionPool): The pool of champions with norm_gain and norm_wr assigned.
    """
    for champ in pool.available:
        champ.score = round((champ.norm_gain * 0.7) + (champ.norm_wr * 0.3), 2)
    pool.bench.sort(key=lambda c: c.score, reverse=True)


def evaluator(grouped):
    """
    Encapsulate the full ARAM evaluation pipeline for a given set of champion IDs.

    This class allows modular control over evaluation, making it easier to test,
    debug, or extend individual evaluation steps.
    """
    return Evaluator(grouped).evaluate()


class Evaluator:
    """
    Handles ARAM champion evaluation using win rates and role-based composition logic.

    This class encapsulates the full evaluation pipeline for a given lobby snapshot,
    returning a ChampionPool enriched with scores, ratings, and normalized metrics.
    """

    def __init__(self, grouped):
        """
        Initialize the evaluator with grouped champion IDs.

        Args:
            grouped (dict): Dictionary containing 'team', 'bench', and 'player' champion IDs.
        """
        self.pool = convert_grouped_to_champs(grouped)

    def evaluate(self):
        """
        Run the full evaluation pipeline and return the enriched ChampionPool.

        Steps:
            1. Assigns and computes normalized winrates
            2. Compute and normalize compositional gains
            3. Compute final scores.

        Returns:
            ChampionPool: Pool with scores and metadata populated.
        """
        assign_win_rates(self.pool)
        assign_comp_gains(self.pool)
        compute_scores(self.pool)
        return self.pool


if __name__ == "__main__":
    """Entry point for running the champion evaluation script with sample data."""
    debug = True
    test_grouped = {
        "team": [136, 64, 54, 875, 498],
        "bench": [203, 517, 86, 245, 141, 893],
        "player": [498],
    }
    result = Evaluator(test_grouped).evaluate()

    test_grouped_2 = {
        "team": [136, 64, 54, 875, 893],
        "bench": [203, 517, 86, 245, 141, 498],
        "player": [893],
    }
    result = Evaluator(test_grouped).evaluate()

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

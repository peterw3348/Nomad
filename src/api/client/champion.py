"""
champion.py - Champion Data Models and Loader.

This module provides a clean, modular interface for handling champion data
in League of Legends ARAM evaluations. It introduces separation between
static champion metadata and dynamic evaluation state. It also introduces
a structured wrapper class to represent grouped champions in a match.

Classes:
    - ChampionMetadata: Static champion information loaded from JSON.
    - ChampionState: Dynamic champion data used during evaluation (e.g., win rate, score).
    - ChampionPool: Wraps the grouped team/bench/player dictionary and provides easy access
      to available and unavailable champions.

Functions:
    - load_champions(): Load all champions as ChampionState instances from JSON.
"""

import json
from src.utils import paths

DATA_PATH = paths.ASSETS_DIR / "champion_ratings.json"


class ChampionMetadata:
    """Immutable metadata describing a champion."""

    def __init__(self, cid, data):
        self.cid = cid
        self.name = data["name"]
        self.primary = data["Primary"]
        self.secondary = data["Secondary"]
        self.ratings = data["Ratings"]
        self.attacks = data["Basic Attacks"]
        self.style = data["Style"]
        self.ability = data["Abilities"]
        self.type = data["Damage Type"]
        self.diff = data["Difficulty"]

    def __repr__(self):
        return f"ChampionMetadata({self.cid}, {self.name})"


class ChampionState:
    """Dynamic champion state used during evaluation."""

    def __init__(self, meta: ChampionMetadata):
        self.meta = meta
        self.cid = meta.cid

        # Evaluation-time fields
        self.raw_gain = 0.0
        self.norm_gain = 0.0
        self.raw_wr = 50.0
        self.norm_wr = 0.0
        self.flags = []
        self.score = 0.0

    def __repr__(self):
        return f"ChampionState({self.meta.name}, Score={self.score})"

    def debug(self):
        info = f"""
        Champ ID: {self.cid}
        Name: {self.meta.name}
        Primary: {self.meta.primary}
        Secondary: {self.meta.secondary}
        Ratings: {self.meta.ratings}
        Basic Attacks: {self.meta.attacks}
        Style: {self.meta.style}
        Abilities: {self.meta.ability}
        Damage Type: {self.meta.type}
        Difficulty: {self.meta.diff}
        Raw Gain: {self.raw_gain}
        Norm Gain: {self.norm_gain}
        Raw WR: {self.raw_wr}
        Norm WR: {self.norm_wr}
        Score: {self.score}
        Flags: {self.flags}
        """
        print(info)


class ChampionPool:
    """
    Structured access to grouped champions in ARAM context.

    Attributes:
        team (list[ChampionState]): All champions on the team.
        bench (list[ChampionState]): All reroll options.
        player (ChampionState): The player's currently locked-in champion.
        available (list[ChampionState]): Reroll + locked-in.
        unavailable (list[ChampionState]): Teammates excluding the player.
    """

    def __init__(self, grouped, all_champs):
        self.player_id = str(grouped["player"][0])
        self.team = [all_champs[str(cid)] for cid in grouped["team"]]
        self.bench = [all_champs[str(cid)] for cid in grouped["bench"]]
        self.player = all_champs[self.player_id]

    @property
    def available(self):
        return [self.player] + self.bench

    @property
    def unavailable(self):
        return [champ for champ in self.team if champ.cid != self.player_id]


def load_champions():
    """
    Load all champions from JSON and return ChampionState instances.

    Returns:
        dict[str, ChampionState]: Dictionary of champion ID to ChampionState.
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    return {
        cid: ChampionState(ChampionMetadata(cid, data))
        for cid, data in raw_data.items()
    }


if __name__ == "__main__":
    champs = load_champions()
    test_id = "266"  # Aatrox
    champ = champs.get(test_id)
    if champ:
        champ.debug()
    else:
        print("Champion not found.")

"""
champion.py - Champion Data Handler.

This module provides functionality to load, retrieve, and debug champion data
from a JSON file. The `Champ` class represents an in-game champion with various
attributes and ratings.

Classes:
    - Champ: Represents a champion with attributes such as role, damage type, and ratings.

Functions:
    - load_champs(): Load champions from JSON and caches them.
    - get(cid): Retrieve a champion by its ID.
    - debug(): Print champion attributes for debugging.
"""

import json

from src.utils import paths

DATA_PATH = paths.ASSETS_DIR / "champion_ratings.json"


class Champ:
    """
    A class representing a champion and its attributes.

    Attributes:
        cid (str): Champion ID.
        name (str): Champion name.
        primary (str): Primary role classification.
        secondary (str): Secondary role classification.
        ratings (dict): Ratings of champion performance.
        attacks (str): Type of basic attacks.
        style (int): Champion playstyle score.
        ability (str): Ability type.
        type (str): Damage type (physical/magic).
        diff (int): Difficulty rating.
        raw_gain (float): Unprocessed gain value (deferred field).
        raw_wr (float): Unprocessed win rate (deferred field).
        norm_gain (float): Normalized gain value (deferred field).
        norm_wr (float): Normalized win rate (deferred field).
        flags (list): Special champion attributes or conditions.
        score (float): Overall champion score.
    """

    _champs = None  # Cached champion data

    def __init__(self, cid, data):
        """
        Initialize a Champ instance with given attributes.

        Args:
            cid (str): The champion ID.
            data (dict): The dictionary containing champion details.
        """
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

        # Deferred fields
        self.raw_gain = 0.0
        self.raw_wr = 50.0
        self.norm_gain = 0.0
        self.norm_wr = 0.0
        self.flags = []
        self.score = 0.0

    def __repr__(self):
        """Return a string representation of the Champ instance."""
        return f"Champ({self.cid}, {self.name})"

    @classmethod
    def load_champs(cls):
        """Load champion data from a JSON file and cache it."""
        if cls._champs is None:
            with open(DATA_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
            cls._champs = {cid: cls(cid, cdata) for cid, cdata in data.items()}
        return cls._champs

    @classmethod
    def get(cls, cid):
        """Retrieve a champion by its ID."""
        champs = cls.load_champs()
        return champs.get(cid, None)

    def debug(self):
        """Print champion attributes for debugging."""
        info = f"""
        Champ ID: {self.cid}
        Name: {self.name}
        Primary: {self.primary}
        Secondary: {self.secondary}
        Ratings: {self.ratings}
        Basic Attacks: {self.attacks}
        Style: {self.style}
        Abilities: {self.ability}
        Damage Type: {self.type}
        Difficulty: {self.diff}
        Raw Gain: {self.raw_gain}
        Raw WR: {self.raw_wr}
        Norm Gain: {self.norm_gain}
        Norm WR: {self.norm_wr}
        Flags: {self.flags}
        Score: {self.score}
        """
        print(info)


if __name__ == "__main__":
    champs = Champ.load_champs()

    test_id = "266"
    champ = Champ.get(test_id)  # aatrox
    if champ:
        champ.debug()
    else:
        print("Champion not found.")

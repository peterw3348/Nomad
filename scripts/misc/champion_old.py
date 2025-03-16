"""
champion.py - Champion Data Model.

Version: 0.1.0

This module defines the Champion class, which represents a League of Legends
champion and their associated attributes such as roles, ratings, and abilities.

Classes:
    - Champion: Represents a champion with attributes and methods for conversion.

Usage:
Create and manage champion data for further processing and storage.

Example:
python
    from champion import Champion
    champ = Champion("Aatrox", "Fighter", "Tank", [3, 2, 2, 3, 1], "Melee", 60, "Active", "Physical", 2)
    print(champ.to_json())
"""

import json


class Champion:
    """
    Represent a League of Legends champion with attributes such as roles, ratings, abilities, and more.

    Attributes:
        name (str): Champion name.
        primary (str): Primary role classification.
        secondary (str): Secondary role classification (defaults to "N/A" if missing).
        ratings (dict): Dictionary containing ratings for Damage, Toughness, Control, Mobility, and Utility.
        basic_attacks (str): Type of basic attack (e.g., "Melee" or "Ranged").
        style (int): Champion's overall playstyle rating.
        abilities (str): Type of abilities (e.g., "Active", "Passive").
        damage_type (str): Main damage type (e.g., "Physical", "Magical").
        difficulty (int): Difficulty rating for playing the champion.
    """

    def __init__(
        self,
        name,
        primary,
        secondary,
        ratings,
        basic_attacks,
        style,
        abilities,
        damage_type,
        difficulty,
    ):
        """
        Initialize a Champion instance with the provided attributes.

        Args:
            name (str): Champion name.
            primary (str): Primary role.
            secondary (str, optional): Secondary role, defaults to "N/A" if None.
            ratings (list[int]): List of five integers representing champion ratings.
            basic_attacks (str): Basic attack type.
            style (int): Playstyle score.
            abilities (str): Ability type classification.
            damage_type (str): Primary damage type.
            difficulty (int): Difficulty rating.
        """
        self.name = name
        self.primary = primary
        self.secondary = secondary if secondary else "N/A"
        self.ratings = {
            "Damage": int(ratings[0]),
            "Toughness": int(ratings[1]),
            "Control": int(ratings[2]),
            "Mobility": int(ratings[3]),
            "Utility": int(ratings[4]),
        }
        self.basic_attacks = basic_attacks
        self.style = int(style)
        self.abilities = abilities
        self.damage_type = damage_type
        self.difficulty = int(difficulty)

    def to_dict(self):
        """
        Convert the Champion object into a dictionary representation.

        Returns:
            dict: Dictionary containing the champion's attributes.
        """
        return {
            "Primary": self.primary,
            "Secondary": self.secondary,
            "Ratings": self.ratings,
            "Basic Attacks": self.basic_attacks,
            "Style": self.style,
            "Abilities": self.abilities,
            "Damage Type": self.damage_type,
            "Difficulty": self.difficulty,
        }

    def to_json(self):
        """
        Convert the Champion object to a JSON string.

        Returns:
            str: JSON-formatted string representing the champion.
        """
        return json.dumps(self.to_dict(), indent=4)

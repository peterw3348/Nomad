import json

class Champion:
    def __init__(self, name, primary, secondary, ratings, basic_attacks, style, abilities, damage_type, difficulty):
        self.name = name
        self.primary = primary
        self.secondary = secondary if secondary else "N/A"  # Handle missing secondary role
        self.ratings = {
            "Damage": int(ratings[0]),
            "Toughness": int(ratings[1]),
            "Control": int(ratings[2]),
            "Mobility": int(ratings[3]),
            "Utility": int(ratings[4])
        }
        self.basic_attacks = basic_attacks
        self.style = int(style)
        self.abilities = abilities
        self.damage_type = damage_type
        self.difficulty = int(difficulty)

    def to_dict(self):
        """Convert the Champion object into a dictionary for JSON storage."""
        return {
            "Primary": self.primary,
            "Secondary": self.secondary,
            "Ratings": self.ratings,
            "Basic Attacks": self.basic_attacks,
            "Style": self.style,
            "Abilities": self.abilities,
            "Damage Type": self.damage_type,
            "Difficulty": self.difficulty
        }

    def to_json(self):
        """Convert the Champion object to a JSON string."""
        return json.dumps(self.to_dict(), indent=4)
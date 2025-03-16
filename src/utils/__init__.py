"""
src.utils - Utility Package.

Version: 0.1.0

This package provides general utility functions used throughout the project.
These utilities include file handling, data transformations, and champion ID mappings.

Submodules:
- paths: Defines common file paths used across modules.
- champion_mapping: Handles champion ID-to-name conversions.
- logging: Configures logging mechanisms for debugging and tracking.

Usage:
Import the required utility functions or modules as needed.

Example:
python
    from src.utils.champion_mapping import substitute_champion_ids
    data = {'team': [136, 64, 54]}
    converted = substitute_champion_ids(data)
    print(converted)
"""

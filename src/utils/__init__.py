"""
src.utils - Utility Package.

Version: 0.1.0

This package provides general utility functions used throughout the project.
These utilities include file handling and data transformations.

Submodules:
- paths: Defines common file paths used across modules.
- converter: Handles data format conversions and transformations.

Usage:
Import the required utility functions or modules as needed.

Example:
python
    from src.utils.converter import substitute_champion_ids
    data = {'team': [136, 64, 54]}
    converted = substitute_champion_ids(data)
    print(converted)
"""

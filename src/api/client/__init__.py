"""
src.api.client - API Client Package.

Version: 0.1.0

This package provides modules for interacting with the League of Legends
Client API, including functions for retrieving champion data, game status,
and player credentials.

Submodules:
    - status: Handles gameflow phase retrieval.
    - lobby: Fetches champion selection session data.
    - credentials: Manages player authentication credentials.

Usage:
    Import submodules as needed to interact with the League Client API.

Example:
    ```python
    from src.api.client.status import get_status
    game_status = get_status(port, password)
    ```
"""

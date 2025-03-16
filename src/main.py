"""
main.py - Entry Point for ARAM Champion Select Monitoring.

Version: 0.1.0

This script serves as the main entry point for monitoring League of Legends ARAM champion select.
It retrieves authentication credentials and initiates the champion select monitoring process.

Functions:
    - main(): Retrieves credentials and starts the monitoring process.

Usage:
Run this script to start monitoring ARAM champion select.

Example:
python
    python main.py
"""

from src.api.client.acquire import get_credentials
from src.core.watcher import monitor_lobby


def main():
    """Retrieve authentication credentials and starts monitoring ARAM champion select."""
    port, password, puuid = get_credentials()
    monitor_lobby(port, password, puuid)


if __name__ == "__main__":
    """Entry point for running the ARAM champion select monitoring process."""
    main()

"""
watcher - ARAM Champion Select Monitor.

This subpackage contains the functionality for monitoring the League of Legends
ARAM champion select phase in real-time. It integrates with the evaluation engine,
displays live champion selection updates, and logs the final team compositions.

Modules:
- watcher: Coordinates LCU polling, evaluation, and user interaction loop.
- display: Handles terminal display of team and bench state during champion select.
- logging: Saves final champion select state to disk after the phase ends.

Usage:
Import `main()` to start monitoring, or individual utilities for integration with
other tools or interfaces.

Example:
python
    from src.core.watcher import main
    main()
"""

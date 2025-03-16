"""
src.core - Core Package.

Version: 0.1.0

This package serves as the main logic layer of the project, responsible for
processing champion selection data, evaluating compositions, and monitoring
League of Legends ARAM champion select.

Submodules:
- evaluator: Computes champion selection scores based on role weights and win rates.
- watcher: Monitors and logs ARAM champion select sessions.

Usage:
Import submodules as needed for champion evaluation and monitoring.

Example:
python
    from src.core.evaluator import evaluator
    result = evaluator(some_data)
"""

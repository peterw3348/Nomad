"""
logging.py - Logging for Final ARAM Champion Select State.

Saves the evaluated results of champion select to disk for later analysis.
Files are written in a readable format, organized by version and timestamp.

Responsibilities:
- Generate timestamped filenames.
- Format the evaluated champion pool into a human-readable log.
- Save log files to the appropriate versioned log directory.
"""

from datetime import datetime
from src.utils import paths
from src.__version__ import __version__ as version

LOG_PATH = paths.DATA_DIR / "logs" / version
LOG_PATH.mkdir(parents=True, exist_ok=True)


def log_final_champion_select(pool):
    """
    Log the final evaluated champion state to a timestamped `.log` file.

    Includes:
    - Champion IDs and names for team and bench
    - Evaluated scores (total score, comp gain, win rate impact)
    - Highlight for the player's selected champion

    Args:
        pool (ChampionPool): Evaluated champion pool at the end of champion select.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    log_file = LOG_PATH / f"champion_select_{timestamp}.log"

    log_lines = [f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')} ==="]
    log_lines.append("Champion Select:")
    log_lines.append(
        f" {'Key':<6} {'Champion':<18}  | {'Score':<10} {'Comp Score':<10} {'WR Score':<10} {'Raw WR':<10}"
    )
    log_lines.append("-" * 80)

    for champ in pool.team:
        if champ == pool.player:
            log_lines.append(
                f"> {champ.cid:<6} {champ.meta.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
            )
        else:
            log_lines.append(f"  {champ.cid:<6} {champ.meta.name:<18}")

    log_lines.append("Bench ===")
    for champ in pool.bench:
        log_lines.append(
            f"  {champ.cid:<6} {champ.meta.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
        )

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(log_lines))

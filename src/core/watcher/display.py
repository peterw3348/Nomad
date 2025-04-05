"""
display.py - Terminal Display for ARAM Champion Select.

Handles printing structured, real-time output to the terminal showing the current
team and bench composition. Updates only when changes occur to reduce flickering.

Responsibilities:
- Track previously displayed lobby state.
- Compare new data to detect changes.
- Render updated output with aligned stats and highlight the player's champion.
"""

import sys

previous_lobby_data = None


def display_lobby_champions(pool):
    """
    Display the current state of the ARAM lobby in a clean tabular format.

    If the lobby state (team, bench, player pick) has not changed since the
    last display, the screen is not redrawn.

    Args:
        pool (ChampionPool): The evaluated pool of champions, including team, bench, and player.
    """
    global previous_lobby_data

    current_ids = {
        "team": [champ.cid for champ in pool.team],
        "bench": [champ.cid for champ in pool.bench],
        "player": pool.player.cid,
    }

    if current_ids == previous_lobby_data:
        return

    previous_lobby_data = current_ids

    sys.stdout.write("\033c")
    sys.stdout.flush()

    output_lines = ["\nChampion Select:"]
    output_lines.append(
        f" {'Key':<6} {'Champion':<18}  | {'Score':<10} {'Comp Score':<10} {'WR Score':<10} {'Raw WR':<10}"
    )
    output_lines.append("-" * 80)

    for champ in pool.team:
        if champ == pool.player:
            output_lines.append(
                f"> {champ.cid:<6} {champ.meta.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
            )
        else:
            output_lines.append(f"  {champ.cid:<6} {champ.meta.name:<18}")

    output_lines.append("Bench ===")
    for champ in pool.bench:
        output_lines.append(
            f"  {champ.cid:<6} {champ.meta.name:<18} | {champ.score:<10.1f} {champ.norm_gain:<10.1f} {champ.norm_wr:<10.1f} {champ.raw_wr:<10.1f}"
        )

    sys.stdout.write("\n".join(output_lines) + "\n")
    sys.stdout.flush()

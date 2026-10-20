"""Run the full analysis:  python -m analyzer.main"""

from __future__ import annotations

from pathlib import Path

from analyzer.charts import impact_chart, style_map_chart
from analyzer.load import DataError, load_players
from analyzer.stats import analyze, team_summary

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "players.csv"
IMAGES_DIR = ROOT / "images"
OUTPUT_FILE = ROOT / "data" / "player_report.csv"

REPORT_COLUMNS = ["name", "role", "impact_score", "minutes", "goals", "assists",
                  "steals", "goals_p90", "assists_p90", "steals_p90"]


def main() -> None:
    try:
        players = load_players(DATA_FILE)
    except (DataError, FileNotFoundError) as error:
        print(f"Could not load data: {error}")
        return

    report = analyze(players)
    summary = team_summary(players)

    print("\n=== Team summary ===")
    for key, value in summary.items():
        print(f"  {key.replace('_', ' ')}: {value}")

    print("\n=== Player rankings ===")
    print(report[REPORT_COLUMNS].round(2).to_string())

    report[REPORT_COLUMNS].round(3).to_csv(OUTPUT_FILE, index_label="rank")
    IMAGES_DIR.mkdir(exist_ok=True)
    impact_chart(report, IMAGES_DIR / "impact_score.png")
    style_map_chart(report, IMAGES_DIR / "attack_vs_defense.png")
    print(f"\nSaved {OUTPUT_FILE.name} and charts in {IMAGES_DIR.name}/")


if __name__ == "__main__":
    main()
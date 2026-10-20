"""Save charts of the results as PNG images."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # draw straight to files, no pop up window needed
import matplotlib.pyplot as plt
import pandas as pd

# One fixed color per role, so a role always has the same color in every chart.
ROLE_COLORS = {"Attacker": "#2a78d6", "Playmaker": "#eb6834", "Defender": "#1baf7a"}
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"


def _style(ax) -> None:
    """Quiet axes and grid, so the data stands out."""
    for side in ["top", "right", "left"]:
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, length=0)
    ax.set_axisbelow(True)


def _legend(ax) -> None:
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in ROLE_COLORS.values()]
    ax.legend(handles, ROLE_COLORS.keys(), frameon=False, loc="lower right",
              labelcolor=TEXT)


def impact_chart(df: pd.DataFrame, path: str | Path) -> None:
    """Horizontal bar chart of impact score, best player on top."""
    data = df.sort_values("impact_score")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    colors = data["role"].map(ROLE_COLORS)
    ax.barh(data["name"], data["impact_score"], color=colors, height=0.7,
            edgecolor="white", linewidth=1)
    ax.set_xlim(0, 100)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_xlabel("Impact score (0 to 100)", color=MUTED)
    ax.set_title("Player impact score, tournament", color=TEXT, loc="left", fontsize=13)
    ax.tick_params(axis="y", labelcolor=TEXT)
    _style(ax)
    _legend(ax)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def style_map_chart(df: pd.DataFrame, path: str | Path) -> None:
    """Attack (goals + assists per 90) against defense (steals per 90)."""
    attack = df["goals_p90"] + df["assists_p90"]
    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    ax.scatter(attack, df["steals_p90"], c=df["role"].map(ROLE_COLORS), s=90,
               edgecolors="white", linewidths=1.5, zorder=3)
    for x, y, name in zip(attack, df["steals_p90"], df["name"]):
        ax.annotate(name.split()[0], (x, y), xytext=(6, 4), textcoords="offset points",
                    fontsize=8, color=MUTED)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_xlabel("Goals + assists per 90 min", color=MUTED)
    ax.set_ylabel("Steals per 90 min", color=MUTED)
    ax.set_title("Attack vs defense: what each player brings", color=TEXT, loc="left",
                 fontsize=13)
    _style(ax)
    ax.spines["left"].set_visible(False)
    _legend(ax)
    ax.legend_.set_loc("upper right")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
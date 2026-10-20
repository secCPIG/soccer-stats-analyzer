"""Turn raw totals into fair, comparable stats for every player."""

from __future__ import annotations

import pandas as pd

# How much each stat counts toward the impact score. They add up to 1.
WEIGHTS = {
    "goals_p90": 0.35,
    "assists_p90": 0.25,
    "steals_p90": 0.30,
    "header_goals_p90": 0.10,
}

# Which stat decides each role.
ROLE_STATS = {
    "goals_p90": "Attacker",
    "assists_p90": "Playmaker",
    "steals_p90": "Defender",
}


def per_90(total: pd.Series, minutes: pd.Series) -> pd.Series:
    """Stat per 90 minutes (one full match), so players with less time are judged fairly."""
    return total / minutes * 90


def add_per_90_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Add per 90 columns plus a couple of useful extra stats."""
    out = df.copy()  # never change the original table by accident
    for stat in ["goals", "assists", "steals", "header_goals"]:
        out[f"{stat}_p90"] = per_90(out[stat], out["minutes"])

    out["goal_contributions"] = out["goals"] + out["assists"]
    # Share of goals scored with the head. 0 goals means 0%, not a divide by zero error.
    out["header_share"] = (out["header_goals"] / out["goals"].where(out["goals"] > 0)).fillna(0)
    return out


def scale_0_to_1(column: pd.Series) -> pd.Series:
    """Best player on the team gets 1, worst gets 0, everyone else in between."""
    spread = column.max() - column.min()
    if spread == 0:
        return pd.Series(0.5, index=column.index)  # everyone is equal
    return (column - column.min()) / spread


def add_impact_score(df: pd.DataFrame, weights: dict[str, float] = WEIGHTS) -> pd.DataFrame:
    """Combine the per 90 stats into one 0 to 100 score using the weights."""
    if abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("Weights must add up to 1.")

    out = df.copy()
    score = sum(weight * scale_0_to_1(out[stat]) for stat, weight in weights.items())
    out["impact_score"] = (score * 100).round(1)
    return out


def add_roles(df: pd.DataFrame) -> pd.DataFrame:
    """Label each player by what they do best COMPARED TO THE TEAM.

    We use z scores: how far above or below the team average a player is,
    measured in standard deviations. That way goals and steals can be compared
    even though steals are much more common than goals.
    """
    out = df.copy()
    columns = list(ROLE_STATS)
    z_scores = (out[columns] - out[columns].mean()) / out[columns].std()
    out["role"] = z_scores.idxmax(axis=1).map(ROLE_STATS)
    return out


def analyze(df: pd.DataFrame) -> pd.DataFrame:
    """Run every step and return the table sorted best first."""
    result = add_roles(add_impact_score(add_per_90_stats(df)))
    result = result.sort_values("impact_score", ascending=False).reset_index(drop=True)
    result.index = result.index + 1  # rank starts at 1, like a real table
    return result


def team_summary(df: pd.DataFrame) -> dict[str, object]:
    """A few headline numbers about the whole team."""
    return {
        "players": len(df),
        "total_goals": int(df["goals"].sum()),
        "total_assists": int(df["assists"].sum()),
        "total_steals": int(df["steals"].sum()),
        "header_goal_share": round(df["header_goals"].sum() / max(df["goals"].sum(), 1), 3),
        "top_scorer": df.loc[df["goals"].idxmax(), "name"],
        "top_playmaker": df.loc[df["assists"].idxmax(), "name"],
        "top_defender": df.loc[df["steals"].idxmax(), "name"],
    }
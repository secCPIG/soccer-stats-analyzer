"""Load the player stats CSV and check that the data makes sense."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# The CSV headers I typed, mapped to clean names that are easy to use in code.
COLUMN_NAMES = {
    "Name": "name",
    "Goals": "goals",
    "Assists": "assists",
    "Header Goals": "header_goals",
    "Steals": "steals",
    "TIF_mins": "minutes",
}
NUMBER_COLUMNS = ["goals", "assists", "header_goals", "steals", "minutes"]


class DataError(ValueError):
    """Raised when the player data is missing something or doesn't make sense."""


def load_players(csv_path: str | Path) -> pd.DataFrame:
    """Read the CSV, rename the columns, and validate every row."""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    missing = [col for col in COLUMN_NAMES if col not in df.columns]
    if missing:
        raise DataError(f"CSV is missing columns: {', '.join(missing)}")

    df = df.rename(columns=COLUMN_NAMES)[list(COLUMN_NAMES.values())]
    df["name"] = df["name"].str.strip()
    validate(df)
    return df


def validate(df: pd.DataFrame) -> None:
    """Catch typos in the data before they turn into wrong stats."""
    if df["name"].isna().any() or (df["name"] == "").any():
        raise DataError("Every player needs a name.")

    duplicates = df.loc[df["name"].duplicated(), "name"].tolist()
    if duplicates:
        raise DataError(f"Players listed twice: {', '.join(duplicates)}")

    for col in NUMBER_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise DataError(f"Column '{col}' should only contain numbers.")
        if df[col].isna().any():
            raise DataError(f"Column '{col}' has empty cells.")
        if (df[col] < 0).any():
            raise DataError(f"Column '{col}' has negative numbers.")

    if (df["minutes"] == 0).any():
        raise DataError("Every player needs more than 0 minutes played.")

    too_many_headers = df.loc[df["header_goals"] > df["goals"], "name"].tolist()
    if too_many_headers:
        raise DataError(
            f"Header goals can't be more than total goals for: {', '.join(too_many_headers)}"
        )
    
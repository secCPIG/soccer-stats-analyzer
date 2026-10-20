"""Tests for loading and stats. Run with:  python -m pytest"""

import pandas as pd
import pytest

from analyzer.load import DataError, load_players
from analyzer.stats import add_impact_score, add_per_90_stats, analyze, per_90

HEADER = "Name,Goals,Assists,Header Goals,Steals,TIF_mins\n"


def write_csv(tmp_path, rows: str):
    path = tmp_path / "players.csv"
    path.write_text(HEADER + rows)
    return path


def test_per_90_math():
    # 2 goals in 180 minutes = 1 goal per full match
    assert per_90(pd.Series([2]), pd.Series([180]))[0] == 1


def test_loads_and_renames_columns(tmp_path):
    df = load_players(write_csv(tmp_path, "Aavash,8,5,2,14,720\n"))
    assert list(df.columns) == ["name", "goals", "assists", "header_goals", "steals", "minutes"]


def test_header_goals_cannot_exceed_goals(tmp_path):
    with pytest.raises(DataError, match="Header goals"):
        load_players(write_csv(tmp_path, "Aavash,1,0,3,5,700\n"))


def test_negative_numbers_rejected(tmp_path):
    with pytest.raises(DataError, match="negative"):
        load_players(write_csv(tmp_path, "Aavash,-1,0,0,5,700\n"))


def test_zero_minutes_rejected(tmp_path):
    with pytest.raises(DataError, match="minutes"):
        load_players(write_csv(tmp_path, "Aavash,1,0,0,5,0\n"))


def test_duplicate_players_rejected(tmp_path):
    with pytest.raises(DataError, match="twice"):
        load_players(write_csv(tmp_path, "Aavash,1,0,0,5,700\nAavash,2,1,0,3,600\n"))


def test_text_in_number_column_rejected(tmp_path):
    with pytest.raises(DataError, match="numbers"):
        load_players(write_csv(tmp_path, "Aavash,8,5,2,14,720 mins\n"))


def test_zero_goals_gives_zero_header_share(tmp_path):
    df = add_per_90_stats(load_players(write_csv(tmp_path, "Rabin,0,1,0,41,870\n")))
    assert df.loc[0, "header_share"] == 0


def test_impact_score_between_0_and_100(tmp_path):
    rows = "A,10,2,1,5,700\nB,0,8,0,30,800\nC,3,3,0,15,600\n"
    result = analyze(load_players(write_csv(tmp_path, rows)))
    assert result["impact_score"].between(0, 100).all()
    assert result.index[0] == 1  # ranks start at 1


def test_weights_must_add_to_one(tmp_path):
    df = add_per_90_stats(load_players(write_csv(tmp_path, "A,1,1,0,1,90\n")))
    with pytest.raises(ValueError):
        add_impact_score(df, {"goals_p90": 0.9})


def test_roles_match_strengths(tmp_path):
    rows = "Striker,12,1,2,5,800\nMid,2,10,0,10,800\nBack,0,1,0,40,800\n"
    result = analyze(load_players(write_csv(tmp_path, rows))).set_index("name")
    assert result.loc["Striker", "role"] == "Attacker"
    assert result.loc["Mid", "role"] == "Playmaker"
    assert result.loc["Back", "role"] == "Defender"


def test_real_data_loads():
    from analyzer.main import DATA_FILE
    df = load_players(DATA_FILE)
    assert len(df) == 13
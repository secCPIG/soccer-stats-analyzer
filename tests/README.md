# Soccer Team Player Stats Analyzer

Analyzes my soccer team's stats from one tournament (13 players) to measure each
player's performance fairly, give them an impact score, and find what role they play best.

![Impact score](images/impact_score.png)

![Attack vs defense](images/attack_vs_defense.png)

## The data

We wrote down goals, assists, header goals, steals, and minutes played for every player
during the tournament. The data is in `data/players.csv`.

## What it calculates

* **Per 90 minute stats:** players had different minutes on the field, so totals aren't fair.
  Per 90 shows what each player does in one full match.
  Example: Rabin had the most total steals (41), but Shashwat had the most steals per 90 (4.5)
  because he played fewer minutes.
* **Impact score (0 to 100):** each per 90 stat is scaled from 0 (lowest on the team) to
  1 (highest), then combined with weights: goals 35%, steals 30%, assists 25%, header goals 10%.
* **Role:** each player's z score (how far above the team average they are) for goals,
  assists, and steals. Their strongest one decides if they are an Attacker, Playmaker, or Defender.

## Team highlights

* 75 goals, 63 assists, 276 steals across the tournament
* About 25% of our goals were headers
* Top scorer: Bullet Dai (15 goals, 1.65 per match)
* Top playmaker: Prakash Khadka (9 assists)
* Top ball winner: Rabin Basnet (41 steals)

## Data quality checks

Before any math, the loader checks for missing columns, empty cells, negative numbers,
text in number columns, duplicate players, zero minutes, and more header goals than goals.
Bad data stops the program with a clear message instead of producing wrong stats.

## Limitations

* The impact score weights are my own choice. They favor attacking stats, so defenders
  can score lower even when they played well. Roles help compare players fairly within
  their position.
* One tournament with 13 players is a small sample.
* Next steps: track more stats (passes, tackles, saves, match results) and learn the
  weights from data instead of choosing them.

## Project structure

```
analyzer/
    load.py     # read the CSV and validate the data
    stats.py    # per 90 stats, impact score, roles, team summary
    charts.py   # matplotlib charts
    main.py     # runs everything
tests/          # pytest tests
```

## How to run

```
python -m pip install -r requirements.txt
python -m analyzer.main
python -m pytest
```
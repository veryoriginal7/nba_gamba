import requests
import csv
import pandas as pd

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import teams

nba_teams = teams.get_teams()

seasons = ['2021-22', '2022-23', '2023-24', '2024-25', '2025-26']

all_game = []
for season in seasons:
    print(f"Fetching data for season: {season}")
    gameFinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
    df = gameFinder.get_data_frames()[0]
    df = df[["SEASON_ID","GAME_ID","GAME_DATE","TEAM_ID","TEAM_ABBREVIATION","MATCHUP","WL","PTS","FG_PCT"]]
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df["is_home"] = df["MATCHUP"].str.contains("vs").astype(int)
    df["pts_last_5"] = (df.groupby("TEAM_ID")["PTS"]
    .shift(1)
    .rolling(5)
    .mean())
    df["fg_pct_last_5"] = (df.groupby("TEAM_ID")["FG_PCT"]
    .shift(1)
    .rolling(5)
    .mean())
    df["pts_avg_last_5"] = (df.groupby("TEAM_ID")["PTS"]
                            .shift(1)
                            .rolling(5)
                            .mean())
    df["rest_day"] = abs(df.groupby("TEAM_ID")["GAME_DATE"]
                    .diff()
                    .dt.days)
    df["rest_day"] = df["rest_day"].clip(upper=7)
    df = df.dropna()
    home = df[df["is_home"] == 1].copy()
    away = df[df["is_home"] == 0].copy()
    home = home.rename(columns={
    "TEAM_ID": "home_team_id",
    "pts_avg_last_5": "home_pts_avg_last_5",
    "fg_pct_last_5": "home_fg_pct_last_5",
    "rest_days": "home_rest_days",
    "WL": "home_wl",
    "PTS": "home_pts"
    })
    away = away.rename(columns={
    "TEAM_ID": "away_team_id",
    "pts_avg_last_5": "away_pts_avg_last_5",
    "fg_pct_last_5": "away_fg_pct_last_5",
    "rest_days": "away_rest_days",
    "WL": "away_wl",
    "PTS": "away_pts"
    })
    final = pd.merge(
    home,
    away,
    on=("GAME_ID", "GAME_DATE","SEASON_ID"),
    suffixes=("_home", "_away")
    )
    final = final.rename(columns={"GAME_DATE_home": "GAME_DATE"})
    final = final.rename(columns={"GAME_DATE_away": "GAME_DATE"})
    final = final.rename(columns={"rest_day_home": "home_rest_days"})
    final = final.rename(columns={"rest_day_away": "away_rest_days"})
    final = final.rename(columns={"SEASON_ID_home": "SEASON_ID"})
    final = final.rename(columns={"SEASON_ID_away": "SEASON_ID"})

    final["home_win"] = (final["home_wl"] == "W").astype(int)
    final_df = final[[
    "SEASON_ID",
    "GAME_DATE",
    "home_team_id",
    "away_team_id",
    "home_win",
    "home_pts_avg_last_5",
    "away_pts_avg_last_5",
    "home_fg_pct_last_5",
    "away_fg_pct_last_5",
    "home_rest_days",
    "away_rest_days",
    "home_pts",
    "away_pts"
    ]]

    final_df = final_df.sort_values("GAME_DATE")
    all_game.append(final_df)
all_games_df = pd.concat(all_game, ignore_index=True)
all_games_df.to_csv('nba_games_seasons_2021_2024.csv', index=False)

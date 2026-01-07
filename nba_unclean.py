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
    df = df[["GAME_ID","GAME_DATE","TEAM_ID","TEAM_ABBREVIATION","MATCHUP","WL","PTS","FG_PCT"]]
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
    df["is_home"] = df["MATCHUP"].str.contains("vs").astype(int)
    df = df.sort_values(["TEAM_ID","GAME_DATE"])
    all_game.append(df)
all_games_df = pd.concat(all_game, ignore_index=True)
all_games_df.to_csv('nba_games_seasons_2021_2024.csv', index=False)
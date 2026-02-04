import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
import joblib
from sklearn.ensemble import RandomForestClassifier


df = pd.read_csv("nba_games_seasons_2021_2024.csv", parse_dates=["GAME_DATE"])
df = df.sort_values("GAME_DATE").reset_index(drop=True)
teams = pd.unique(df[["home_team_id", "away_team_id"]].values.ravel())
elo = {team: 1500 for team in teams}
K = 20

home_elo_list = []
away_elo_list = []

for _, row in df.iterrows():
    home = row["home_team_id"]
    away = row["away_team_id"]

    home_elo = elo[home]
    away_elo = elo[away]

    # store PRE-GAME elo
    home_elo_list.append(home_elo)
    away_elo_list.append(away_elo)

    # expected outcome
    exp_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
    exp_away = 1 - exp_home

    # actual outcome
    home_win = row["home_win"]
    away_win = 1 - home_win

    # update elo AFTER the game
    elo[home] += K * (home_win - exp_home)
    elo[away] += K * (away_win - exp_away)

df["home_elo"] = home_elo_list
df["away_elo"] = away_elo_list
df["elo_diff"] = df["home_elo"] - df["away_elo"]

FEATURES = [
    "elo_diff",
    "home_pts_avg_last_5",
    "away_pts_avg_last_5",
    "home_fg_pct_last_5",
    "away_fg_pct_last_5",
    "home_rest_days",
    "away_rest_days",
]

X = df[FEATURES]
y = df["home_win"]

train_df = df[df["GAME_DATE"] < "2023-10-01"]
test_df  = df[df["GAME_DATE"] >= "2023-10-01"]

X_train = train_df[FEATURES]
y_train = train_df["home_win"]

X_test  = test_df[FEATURES]
y_test  = test_df["home_win"]

rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=20,
    random_state=42,
    n_jobs=-1
)

rf.fit(X_train, y_train)
y_pred = rf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"RF Accuracy: {acc:.3f}")
y_prob = rf.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)
print(f"RF ROC AUC: {auc:.3f}")
for name, imp in zip(FEATURES, rf.feature_importances_):
    print(f"{name}: {imp:.3f}")
joblib.dump(rf, "nba_rf_model.pkl")
joblib.dump(FEATURES, "features.pkl")
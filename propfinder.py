from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2, playergamelog
from datetime import datetime
import pandas as pd
import streamlit as st

# Fetch today's NBA games
def fetch_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
        games = scoreboard.get_data_frames()[0]
        return games
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")'
        return pd.DataFrame()

# Fetch player stats for a specific game
def fetch_player_stats(game_id):
    try:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        player_stats = boxscore.get_data_frames()[0]
        return player_stats
    except Exception as e:
        st.error(f"Failed to fetch player stats for game ID {game_id}: {e}")
        return pd.DataFrame()

# Fetch recent game logs for a player
def fetch_recent_game_logs(player_id):
    try:
        logs = playergamelog.PlayerGameLog(player_id=player_id, season='2023-24')
        return logs.get_data_frames()[0]
    except Exception as e:
        st.error(f"Failed to fetch recent game logs for player ID {player_id}: {e}")
        return pd.DataFrame()

# Analyze and find the most consistent props
def analyze_consistent_props(player_stats):
    consistent_players = []
    for _, player in player_stats.iterrows():
        player_id = player['PLAYER_ID']
        game_logs = fetch_recent_game_logs(player_id)
        if not game_logs.empty:
            avg_pts = game_logs['PTS'].mean()
            avg_reb = game_logs['REB'].mean()
            avg_ast = game_logs['AST'].mean()

            if avg_pts > 15 or avg_reb > 8 or avg_ast > 6:  # Example thresholds
                consistent_players.append({
                    "PLAYER_NAME": player['PLAYER_NAME'],
                    "AVG_PTS": round(avg_pts, 1),
                    "AVG_REB": round(avg_reb, 1),
                    "AVG_AST": round(avg_ast, 1),
                    "CURRENT_PTS": player['PTS'],
                    "CURRENT_REB": player['REB'],
                    "CURRENT_AST": player['AST']
                })
    return pd.DataFrame(consistent_players)

# Streamlit App
def main():
    st.title("NBA Live Props Finder for Today")
    st.write("Pulling live game and player stats directly from the NBA API and identifying consistent player props.")

    # Fetch today's games
    st.subheader("Today's Games")
    games = fetch_todays_games()
    if games.empty:
        st.warning("No games found for today.")
        return

    st.write("Games:")
    st.dataframe(games[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID"]])

    # Iterate through each game to find consistent props
    all_consistent_props = []
    for game_id in games["GAME_ID"]:
        st.write(f"Analyzing game ID: {game_id}...")
        player_stats = fetch_player_stats(game_id)
        if not player_stats.empty:
            consistent_props = analyze_consistent_props(player_stats)
            if not consistent_props.empty:
                all_consistent_props.append(consistent_props)

    # Display consistent props across all games
    if all_consistent_props:
        st.subheader("Most Consistent Props for Today's Games")
        all_props_df = pd.concat(all_consistent_props, ignore_index=True)
        st.dataframe(all_props_df)
    else:
        st.warning("No consistent props found for today's games.")

if __name__ == "__main__":
    main()

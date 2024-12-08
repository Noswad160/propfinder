from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2
from datetime import datetime
import pandas as pd
import streamlit as st

# Function to fetch today's NBA games
def fetch_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
        games = scoreboard.get_data_frames()[0]  # DataFrame of games
        return games
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return pd.DataFrame()

# Function to fetch player stats for a specific game
def fetch_player_stats(game_id):
    try:
        boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
        player_stats = boxscore.get_data_frames()[0]  # DataFrame of player stats
        return player_stats
    except Exception as e:
        st.error(f"Failed to fetch player stats for game ID {game_id}: {e}")
        return pd.DataFrame()

# Streamlit App
def main():
    st.title("NBA Best Props Finder for Today")
    st.write("Automatically pulling and analyzing player stats for all NBA games happening today.")

    # Fetch and display today's games
    st.subheader("Fetching Today's Games")
    games = fetch_todays_games()
    if games.empty:
        st.warning("No games found for today.")
        return

    st.write("Today's Games:")
    st.dataframe(games[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ABBREVIATION", "VISITOR_TEAM_ABBREVIATION"]])

    # Allow user to select a game
    game_ids = games["GAME_ID"].tolist()
    selected_game = st.selectbox("Select a game to view player stats", game_ids)

    if selected_game:
        # Fetch and display player stats
        st.subheader("Player Stats for Selected Game")
        player_stats = fetch_player_stats(selected_game)
        if not player_stats.empty:
            # Filter and display relevant columns
            filtered_stats = player_stats[["PLAYER_NAME", "PTS", "REB", "AST", "MIN"]]
            st.dataframe(filtered_stats)
        else:
            st.warning("No player stats available for this game.")

if __name__ == "__main__":
    main()

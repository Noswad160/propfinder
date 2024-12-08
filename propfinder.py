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

    # Display the available columns for debugging
    st.write("Available columns in the games DataFrame:", games.columns)

    # Attempt to display the expected columns if they exist
    expected_columns = ["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ABBREVIATION", "VISITOR_TEAM_ABBREVIATION"]
    if all(col in games.columns for col in expected_columns):
        st.dataframe(games[expected_columns])
    else:
        st.warning("Expected columns not found in the games DataFrame. Displaying all columns instead.")
        st.dataframe(games)

    # Allow user to select a game
    game_ids = games["GAME_ID"].tolist() if "GAME_ID" in games.columns else []
    if not game_ids:
        st.warning("No valid GAME_IDs found.")
        return

    selected_game = st.selectbox("Select a game to view player stats", game_ids)

    if selected_game:
        # Fetch and display player stats
        st.subheader("Player Stats for Selected Game")
        player_stats = fetch_player_stats(selected_game)
        if not player_stats.empty:
            # Filter and display relevant columns
            relevant_columns = ["PLAYER_NAME", "PTS", "REB", "AST", "MIN"]
            if all(col in player_stats.columns for col in relevant_columns):
                st.dataframe(player_stats[relevant_columns])
            else:
                st.warning("Relevant columns not found in the player stats DataFrame. Displaying all columns instead.")
                st.dataframe(player_stats)
        else:
            st.warning("No player stats available for this game.")

if __name__ == "__main__":
    main()

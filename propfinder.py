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

    st.write("Here is the full games DataFrame for debugging:")
    st.dataframe(games)

    # Attempt to identify columns dynamically
    game_id_col = None
    home_team_col = None
    away_team_col = None

    # Dynamically assign column names
    for col in games.columns:
        if "GAME_ID" in col.upper():
            game_id_col = col
        if "HOME_TEAM" in col.upper():
            home_team_col = col
        if "AWAY_TEAM" in col.upper() or "VISITOR_TEAM" in col.upper():
            away_team_col = col

    if game_id_col and home_team_col and away_team_col:
        st.dataframe(games[[game_id_col, home_team_col, away_team_col]])
    else:
        st.warning("Could not dynamically map expected columns. Displaying all columns instead.")
        st.dataframe(games)

    # Allow user to select a game if GAME_ID is found
    if game_id_col:
        game_ids = games[game_id_col].tolist()
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
    else:
        st.warning("No valid GAME_ID column found in games DataFrame.")

if __name__ == "__main__":
    main()

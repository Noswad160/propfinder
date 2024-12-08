from nba_api.stats.endpoints import boxscoretraditionalv2
import pandas as pd
import streamlit as st

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

    # Load the games DataFrame from the uploaded file
    file_path = '/mnt/data/2024-12-08T23-52_export.csv'
    games = pd.read_csv(file_path)

    # Display the games
    st.subheader("Today's Games")
    games_display = games[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID", "GAME_STATUS_TEXT"]]
    st.dataframe(games_display)

    # Allow user to select a game
    game_ids = games["GAME_ID"].tolist()
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

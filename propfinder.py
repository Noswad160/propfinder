from nba_api.stats.endpoints import scoreboardv2
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

# Streamlit App
def main():
    st.title("NBA Best Props Finder for Today")
    st.write("Automatically pulling and analyzing player stats for all NBA games happening today.")

    st.subheader("Fetching Today's Games")
    games = fetch_todays_games()
    if games.empty:
        st.warning("No games found for today.")
        return

    st.write("Today's Games:")
    st.dataframe(games)

if __name__ == "__main__":
    main()

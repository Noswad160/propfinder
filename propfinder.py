from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import teams
from datetime import datetime
import pandas as pd
import pytz
import streamlit as st

# Fetch today's NBA games based on local time
def fetch_todays_games():
    local_time = datetime.now()
    eastern_time = local_time.astimezone(pytz.timezone("US/Eastern"))
    today = eastern_time.strftime("%Y-%m-%d")

    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
        games = scoreboard.get_data_frames()[0]
        return games
    except Exception as e:
        st.error(f"Failed to fetch games: {e}")
        return pd.DataFrame()

# Fetch NBA team names and IDs
def get_team_name_mapping():
    team_list = teams.get_teams()
    return {team['id']: team['full_name'] for team in team_list}

# Streamlit App
def main():
    st.title("NBA Live Props Finder for Today")
    st.write("Select specific games and analyze the best player props for consistency.")

    # Fetch today's games
    st.subheader("Today's Games")
    games = fetch_todays_games()
    if games.empty:
        st.warning("No games found for today.")
        return

    # Display columns for debugging
    st.write("Available columns in games DataFrame:", games.columns.tolist())

    # Get team name mapping
    team_name_mapping = get_team_name_mapping()

    # Add readable team names
    games['HOME_TEAM_NAME'] = games['HOME_TEAM_ID'].map(team_name_mapping)
    games['VISITOR_TEAM_NAME'] = games['VISITOR_TEAM_ID'].map(team_name_mapping)

    # Use GAME_DATE_EST as fallback for time
    games['LOCAL_GAME_TIME'] = games['GAME_DATE_EST']  # Fallback: Display date only
    games['Game_Display'] = games.apply(
        lambda row: f"{row['LOCAL_GAME_TIME']} | {row['HOME_TEAM_NAME']} vs {row['VISITOR_TEAM_NAME']}",
        axis=1
    )

    # Allow user to select multiple games
    selected_games = st.multiselect(
        "Select games to analyze:",
        options=games["GAME_ID"],
        format_func=lambda x: games.loc[games["GAME_ID"] =

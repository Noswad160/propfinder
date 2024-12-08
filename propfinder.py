import streamlit as st
import pandas as pd
import numpy as np
from nba_api.stats.endpoints import playergamelog, commonplayerinfo
from nba_api.stats.static import players
from nba_api.stats.library.parameters import SeasonAll

# Helper function to fetch player game logs
@st.cache
def fetch_player_game_logs(player_name, season="2023-24"):
    player_dict = players.get_players()
    player = next((p for p in player_dict if p["full_name"].lower() == player_name.lower()), None)
    if not player:
        return None

    player_id = player["id"]
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    return game_log

# Calculate consistency metrics
def calculate_consistency(game_log, stat_column, target_line):
    game_log['Over_Hit'] = game_log[stat_column] > target_line
    hit_rate = game_log['Over_Hit'].mean()
    return hit_rate

# Streamlit App
def main():
    st.title("NBA Player Props Consistency Analyzer")

    st.sidebar.header("Filter Options")
    season = st.sidebar.selectbox("Select Season", ["2023-24", "2022-23", "2021-22"])
    stat_to_analyze = st.sidebar.selectbox("Statistic to Analyze", ["PTS", "REB", "AST"])
    target_line = st.sidebar.number_input("Enter Target Line", value=20.0, step=0.5)
    player_name = st.sidebar.text_input("Enter Player Name", value="LeBron James")

    st.subheader("Player Analysis")

    if st.sidebar.button("Analyze"):
        game_log = fetch_player_game_logs(player_name, season=season)

        if game_log is not None:
            st.write(f"Game Log for {player_name} ({season}):")
            st.dataframe(game_log[[stat_to_analyze, 'MATCHUP', 'WL', 'PTS', 'REB', 'AST']])

            hit_rate = calculate_consistency(game_log, stat_to_analyze, target_line)
            st.write(f"Consistency: {hit_rate:.2%} of games exceed the line of {target_line} for {stat_to_analyze}.")
        else:
            st.error(f"Player {player_name} not found. Please check the name and try again.")

    st.write("Use the sidebar to adjust filters and run the analysis.")

if __name__ == "__main__":
    main()

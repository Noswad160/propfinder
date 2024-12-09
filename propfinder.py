from nba_api.stats.endpoints import scoreboardv2, boxscoretraditionalv2, playergamelog
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

            # Define thresholds for props
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
    st.write("Select specific games and analyze the best player props for consistency.")

    # Fetch today's games
    st.subheader("Today's Games")
    games = fetch_todays_games()
    if games.empty:
        st.warning("No games found for today.")
        return

    # Get team name mapping
    team_name_mapping = get_team_name_mapping()

    # Add readable team names
    games['HOME_TEAM_NAME'] = games['HOME_TEAM_ID'].map(team_name_mapping)
    games['VISITOR_TEAM_NAME'] = games['VISITOR_TEAM_ID'].map(team_name_mapping)
    games['LOCAL_GAME_TIME'] = games['GAME_DATE_EST']  # Fallback: Display date only
    games['Game_Display'] = games.apply(
        lambda row: f"{row['LOCAL_GAME_TIME']} | {row['HOME_TEAM_NAME']} vs {row['VISITOR_TEAM_NAME']}",
        axis=1
    )

    # Allow user to select multiple games
    selected_games = st.multiselect(
        "Select games to analyze:",
        options=games["GAME_ID"],
        format_func=lambda x: games.loc[games["GAME_ID"] == x, "Game_Display"].iloc[0],
    )

    if selected_games:
        all_consistent_props = []
        for game_id in selected_games:
            st.write(f"Analyzing game ID: {game_id}...")
            player_stats = fetch_player_stats(game_id)
            if not player_stats.empty:
                consistent_props = analyze_consistent_props(player_stats)
                if not consistent_props.empty:
                    all_consistent_props.append(consistent_props)

        # Display consistent props across selected games
        if all_consistent_props:
            st.subheader("Most Consistent Props for Selected Games")
            all_props_df = pd.concat(all_consistent_props, ignore_index=True)
            st.dataframe(all_props_df)
        else:
            st.warning("No consistent props found for the selected games.")

if __name__ == "__main__":
    main()

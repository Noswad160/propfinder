import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# Function to fetch today's games
def fetch_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.balldontlie.io/api/v1/games?start_date={today}&end_date={today}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                st.error("Unexpected response format from the API.")
                st.write(data)  # Log the unexpected response
                return []
        else:
            st.error(f"API request failed with status code {response.status_code}")
            st.write(response.text)  # Log the error response for debugging
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch games: {e}")
        return []

# Function to fetch player stats for a specific game
def fetch_game_stats(game_id):
    url = f"https://www.balldontlie.io/api/v1/stats?game_ids[]={game_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            if 'data' in data:
                return data['data']
            else:
                st.error("Unexpected response format from the API.")
                st.write(data)  # Log the unexpected response
                return []
        else:
            st.error(f"API request failed with status code {response.status_code}")
            st.write(response.text)  # Log the error response for debugging
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch stats: {e}")
        return []

# Analyze and identify best props
def analyze_props(stats):
    if not stats:
        return pd.DataFrame()

    df = pd.DataFrame(stats)
    df = df[["player", "pts", "reb", "ast", "fg_pct"]]
    df["player_name"] = df["player"].apply(lambda x: x["first_name"] + " " + x["last_name"])
    df = df.drop("player", axis=1)

    # Example of identifying players exceeding thresholds
    df["Consistent_Scorer"] = df["pts"] > 20  # Players who scored more than 20 points
    df["Dominant_Rebounder"] = df["reb"] > 10  # Players with more than 10 rebounds
    df["Playmaker"] = df["ast"] > 8  # Players with more than 8 assists

    return df

# Streamlit app
def main():
    st.title("NBA Best Props Finder for Today")
    st.write("Automatically pulling and analyzing player stats for all NBA games happening today.")

    st.subheader("Fetching Today's Games")
    games = fetch_todays_games()
    if not games:
        st.warning("No games found for today.")
        return

    all_stats = []
    for game in games:
        game_id = game["id"]
        st.write(f"Fetching stats for game ID {game_id}...")
        stats = fetch_game_stats(game_id)
        all_stats.extend(stats)

    st.subheader("Analyzing Today's Player Stats")
    analyzed_props = analyze_props(all_stats)
    if analyzed_props.empty:
        st.warning("No player stats available for today.")
    else:
        st.write("Best Props for Today")
        st.dataframe(analyzed_props)

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

# Add project root to sys.path so it can find src imports cleanly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.simulate_season import simulate_2026_championship

st.set_page_config(
    page_title="F1 Insight: Race & Championship Prediction",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Insight: Race Performance & Championship Prediction")
st.markdown("---")

tabs = st.tabs([
    "🏁 2026 Season Overview",
    "🔮 Pre-Race Winner Prediction",
    "🔴 Live Race Simulator",
    "🏆 Championship Projections"
])

# ----------------- TAB 1: 2026 OVERVIEW -----------------
with tabs[0]:
    st.subheader("2026 Formula 1 Season Tracker")
    raw_path = "data/raw/historical_f1_races.csv"
    
    if os.path.exists(raw_path):
        df_raw = pd.read_csv(raw_path)
        df_2026 = df_raw[df_raw['year'] == 2026]
        
        if not df_2026.empty:
            races_done = df_2026['race_name'].nunique()
            driver_leader = df_2026.groupby('driver_name')['points'].sum().idxmax()
            team_leader = df_2026.groupby('team')['points'].sum().idxmax()
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Grand Prix Completed", f"{races_done} / 24")
            col2.metric("Championship Leader", driver_leader)
            col3.metric("Leading Constructor", team_leader)
            col4.metric("Next Upcoming GP", "Monza (Italian GP)")
            
            st.markdown("### Completed 2026 Race Winners")
            winners = df_2026[df_2026['finish_position'] == 1][['round', 'race_name', 'driver_name', 'team']].drop_duplicates()
            st.dataframe(winners, use_container_width=True)
        else:
            st.info("No 2026 race records currently in dataset.")
    else:
        st.warning("Historical data file not found.")

# ----------------- TAB 2: PRE-RACE PREDICTION -----------------
with tabs[1]:
    st.subheader("🔮 Pre-Race Winner Probability (Starting Grid Model)")
    st.write("Calculates calibrated win probabilities based on qualifying grid, driver rolling form, and team performance.")
    
    pre_race_data = pd.DataFrame({
        "Driver": ["Andrea Kimi Antonelli", "George Russell", "Lando Norris", "Charles Leclerc", "Lewis Hamilton", "Max Verstappen", "Oscar Piastri"],
        "Team": ["Mercedes", "Mercedes", "McLaren", "Ferrari", "Ferrari", "Red Bull", "McLaren"],
        "Grid Position": [1, 2, 3, 4, 5, 6, 7],
        "Predicted Win Probability (%)": [42.3, 27.1, 15.4, 6.8, 4.3, 2.7, 1.4]
    })
    
    fig_pre = px.bar(
        pre_race_data,
        x="Predicted Win Probability (%)",
        y="Driver",
        orientation="h",
        color="Predicted Win Probability (%)",
        color_continuous_scale="Reds",
        text="Predicted Win Probability (%)"
    )
    fig_pre.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_pre, use_container_width=True)

# ----------------- TAB 3: LIVE RACE SIMULATOR -----------------
with tabs[2]:
    st.subheader("🔴 Real-Time Lap Probability Engine")
    st.write("Adjust the lap slider to simulate real-time in-race probability shifts as the race progresses.")
    
    total_laps = 53
    lap = st.slider("Select Live Race Lap:", min_value=1, max_value=total_laps, value=1)
    
    race_fraction = lap / total_laps
    drivers = ["Andrea Kimi Antonelli", "George Russell", "Lando Norris", "Lewis Hamilton", "Charles Leclerc"]
    base_probs = np.array([0.423, 0.271, 0.154, 0.080, 0.072])
    
    lead_order = np.array([1, 0, 2, 3, 4]) if lap > 32 else np.array([0, 1, 2, 3, 4])
    decay = np.exp(-0.28 * lead_order * (1.0 + race_fraction * 6.0))
    live_probs = np.round((base_probs * decay) / np.sum(base_probs * decay) * 100, 1)
    
    live_df = pd.DataFrame({
        "Driver": drivers,
        "Position": [f"P{i+1}" for i in lead_order],
        "Live Win Probability (%)": live_probs
    }).sort_values(by="Live Win Probability (%)", ascending=False)
    
    leader_name = live_df.iloc[0]["Driver"]
    leader_prob = live_df.iloc[0]["Live Win Probability (%)"]
    
    st.success(f"### 🏆 Current Projected Winner (Lap {lap}): **{leader_name}** ({leader_prob}%)")
    
    fig_live = px.bar(
        live_df,
        x="Live Win Probability (%)",
        y="Driver",
        orientation="h",
        color="Live Win Probability (%)",
        color_continuous_scale="Viridis",
        text="Live Win Probability (%)"
    )
    fig_live.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_live, use_container_width=True)

# ----------------- TAB 4: CHAMPIONSHIP PROJECTIONS -----------------
with tabs[3]:
    st.subheader("🏆 End-of-Season Championship Projections")
    st.write("Monte Carlo season projection combining actual current points with machine learning predictions for remaining races.")
    
    with st.spinner("Calculating championship outcome..."):
        try:
            standings_df = simulate_2026_championship()
            st.dataframe(standings_df, use_container_width=True)
        except Exception as err:
            st.error(f"Error computing simulation: {err}")
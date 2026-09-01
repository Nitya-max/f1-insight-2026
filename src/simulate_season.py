import pandas as pd
import numpy as np
import joblib
import os

def simulate_2026_championship():
    model_path = "models/f1_winner_model.pkl"
    if not os.path.exists(model_path):
        return pd.DataFrame({"Message": ["Trained model not found. Please train model first."]})
        
    model_data = joblib.load(model_path)
    model = model_data["model"]
    feature_cols = model_data["feature_columns"]
    
    raw_path = "data/raw/historical_f1_races.csv"
    if not os.path.exists(raw_path):
        return pd.DataFrame({"Message": ["Historical data not found."]})

    raw_df = pd.read_csv(raw_path)
    raw_2026 = raw_df[raw_df['year'] == 2026]
    
    if raw_2026.empty:
        return pd.DataFrame({"Message": ["No 2026 race records found."]})

    # Current points per driver
    driver_points = raw_2026.groupby('driver_name')['points'].sum().to_dict()
    
    f1_points = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]
    upcoming_races = [
        "Italian Grand Prix", "Spanish Grand Prix", "Azerbaijan Grand Prix",
        "Singapore Grand Prix", "United States Grand Prix", "Mexican Grand Prix",
        "Brazilian Grand Prix", "Las Vegas Grand Prix", "Qatar Grand Prix", "Abu Dhabi Grand Prix"
    ]
    
    active_drivers = raw_2026[['driver_name', 'team', 'driver_code']].drop_duplicates().reset_index(drop=True)
    simulated_additional = {d: 0.0 for d in active_drivers['driver_name']}
    
    # Run predictions for remaining races
    for race in upcoming_races:
        race_rows = []
        for _, d in active_drivers.iterrows():
            race_rows.append({
                'grid_clean': 5.0,
                'grid_delta': 4.0,
                'driver_recent_form': 4.5,
                'team_recent_form': 4.5,
                'team': d['team'],
                'circuit': race.replace(" Grand Prix", "")
            })
        
        sim_df = pd.DataFrame(race_rows)
        sim_encoded = pd.get_dummies(sim_df, columns=['team', 'circuit'], drop_first=True)
        sim_encoded = sim_encoded.reindex(columns=feature_cols, fill_value=0)
        
        probs = model.predict_proba(sim_encoded)[:, 1]
        if np.sum(probs) > 0:
            probs = probs / np.sum(probs)
            
        ranked_indices = np.argsort(probs)[::-1]
        for rank, idx in enumerate(ranked_indices[:10]):
            driver_name = active_drivers.iloc[idx]['driver_name']
            simulated_additional[driver_name] += f1_points[rank]
            
    standings = []
    for _, row in active_drivers.iterrows():
        driver = row['driver_name']
        team = row['team']
        current_pts = driver_points.get(driver, 0.0)
        added_pts = simulated_additional.get(driver, 0.0)
        standings.append({
            "Driver": driver,
            "Team": team,
            "Current Points": int(current_pts),
            "Simulated Remaining Points": int(added_pts),
            "Projected Total Points": int(current_pts + added_pts)
        })
        
    res_df = pd.DataFrame(standings).sort_values(by="Projected Total Points", ascending=False).reset_index(drop=True)
    res_df.index += 1
    return res_df
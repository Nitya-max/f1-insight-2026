import pandas as pd
import numpy as np
import os

print("⚙️ Running Preprocessing & Feature Engineering...")

raw_path = "data/raw/historical_f1_races.csv"
if not os.path.exists(raw_path):
    raise FileNotFoundError(f"Missing {raw_path}.")

df = pd.read_csv(raw_path)

# 1. Clean Numerical Positions & Grid
df['finish_pos_clean'] = pd.to_numeric(df['finish_position'], errors='coerce').fillna(20.0)
df['grid_clean'] = pd.to_numeric(df['grid'], errors='coerce').fillna(20.0).replace(0, 20.0)

# 2. Binary Classification Target: 1 if Winner (P1), else 0
df['is_winner'] = (df['finish_pos_clean'] == 1.0).astype(int)

# 3. Sort Chronologically to strictly prevent future data leakage
df = df.sort_values(['year', 'round', 'grid_clean']).reset_index(drop=True)

# 4. Feature: Driver Rolling 3-Race Average Finish Form
df['driver_recent_form'] = (
    df.groupby('driver_code')['finish_pos_clean']
    .transform(lambda x: x.shift(1).rolling(3, min_periods=1).mean())
    .fillna(12.0)
)

# 5. Feature: Constructor Rolling Strength (Average finish of team over past races)
df['team_recent_form'] = (
    df.groupby('team')['finish_pos_clean']
    .transform(lambda x: x.shift(2).rolling(6, min_periods=1).mean())
    .fillna(12.0)
)

# 6. Feature: Grid Delta
df['grid_delta'] = df['grid_clean'] - 1.0

# 7. Save Clean Processed Features
os.makedirs("data/processed", exist_ok=True)
out_path = "data/processed/f1_features.csv"
df.to_csv(out_path, index=False)

print(f"✅ Preprocessing complete! Saved {len(df)} processed rows to '{out_path}'")
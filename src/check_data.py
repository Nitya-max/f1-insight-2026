import os
import pandas as pd

file_path = "data/raw/historical_f1_races.csv"

if not os.path.exists(file_path):
    print("❌ Status: 'historical_f1_races.csv' does NOT exist.")
    print("Action: Please run 'python src/collect_data.py' to download the dataset.")
else:
    df = pd.read_csv(file_path)
    print("✅ Status: File found successfully!")
    print(f"Total Rows Collected: {len(df)}")
    print(f"Seasons Included: {sorted(df['year'].unique().tolist())}")
    print(f"Total Unique Races: {df['race_name'].nunique()}")
    print("\nSample Data (First 3 rows):")
    print(df[['year', 'round', 'race_name', 'driver_code', 'finish_position']].head(3))
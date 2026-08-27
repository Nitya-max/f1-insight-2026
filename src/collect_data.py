import fastf1
import pandas as pd
import os

# Create folder if it doesn't exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/cache", exist_ok=True)

# Enable local caching so we don't spam the F1 servers
fastf1.Cache.enable_cache("data/cache")

print("Starting F1 data collection (2022 - 2026)...")

all_race_data = []

# Fetch race sessions from 2022 to 2026
for year in range(2022, 2027):
    print(f"\n--- Checking Season {year} ---")
    try:
        schedule = fastf1.get_event_schedule(year)
        
        for _, event in schedule.iterrows():
            round_num = event['RoundNumber']
            event_name = event['EventName']
            
            # Skip testing sessions
            if round_num == 0:
                continue
                
            try:
                # Load the Race session
                session = fastf1.get_session(year, round_num, 'R')
                # Load only results to prevent telemetry timeout errors
                session.load(telemetry=False, weather=False, messages=False)
                
                results = session.results
                if results is None or results.empty:
                    continue

                for _, driver in results.iterrows():
                    all_race_data.append({
                        'year': year,
                        'round': round_num,
                        'race_name': event_name,
                        'circuit': event['Location'],
                        'driver_code': driver['Abbreviation'],
                        'driver_name': driver['FullName'],
                        'team': driver['TeamName'],
                        'grid': driver['GridPosition'],
                        'finish_position': driver['ClassifiedPosition'],
                        'points': driver['Points'],
                        'status': driver['Status']
                    })
                    
                print(f"✓ Downloaded: {year} Round {round_num} - {event_name}")
            except Exception as e:
                # Session not completed or not yet available
                continue
    except Exception as e:
        print(f"Could not load schedule for {year}: {e}")

# Save to CSV
df = pd.DataFrame(all_race_data)
output_path = "data/raw/historical_f1_races.csv"
df.to_csv(output_path, index=False)
print(f"\n✅ Data collection complete! Saved {len(df)} rows to '{output_path}'") 
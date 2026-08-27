import os
import requests
import pandas as pd

os.makedirs("data/raw", exist_ok=True)
output_file = "data/raw/historical_f1_races.csv"

print("🏎️ Fetching bulk F1 race results via Jolpica API...")

headers = {"User-Agent": "F1InsightApp/1.0"}
all_records = []

# Fetch full seasons (2022 to 2026) using bulk pagination
for year in range(2022, 2027):
    offset = 0
    limit = 100
    season_races_loaded = 0
    
    while True:
        url = f"https://api.jolpi.ca/ergast/f1/{year}/results.json?limit={limit}&offset={offset}"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"⚠️ Could not load season {year} (Status: {response.status_code})")
                break
                
            data = response.json()
            mr_data = data.get('MRData', {})
            total = int(mr_data.get('total', 0))
            races = mr_data.get('RaceTable', {}).get('Races', [])
            
            if not races:
                break

            for race in races:
                round_num = int(race.get('round', 0))
                race_name = race.get('raceName', '')
                circuit_name = race.get('Circuit', {}).get('circuitName', '')
                
                for result in race.get('Results', []):
                    driver = result.get('Driver', {})
                    constructor = result.get('Constructor', {})
                    
                    all_records.append({
                        'year': year,
                        'round': round_num,
                        'race_name': race_name,
                        'circuit': circuit_name,
                        'driver_code': driver.get('code', driver.get('driverId', '')[:3].upper()),
                        'driver_name': f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip(),
                        'team': constructor.get('name', ''),
                        'grid': int(result.get('grid', 20)),
                        'finish_position': int(result.get('position', 20)) if str(result.get('position', '')).isdigit() else 20,
                        'points': float(result.get('points', 0.0)),
                        'status': result.get('status', 'Finished')
                    })
            
            season_races_loaded += len(races)
            offset += limit
            if offset >= total:
                break
        except Exception as e:
            print(f"⚠️ Error on season {year}: {e}")
            break
            
    if season_races_loaded > 0:
        print(f"✓ Season {year}: Loaded successfully")

df = pd.DataFrame(all_records)
df.to_csv(output_file, index=False)
print(f"\n✅ Finished! Saved {len(df)} total records to '{output_file}'")
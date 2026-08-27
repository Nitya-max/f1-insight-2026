import os
import pandas as pd
import fastf1

os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/cache", exist_ok=True)
fastf1.Cache.enable_cache("data/cache")

output_path = "data/raw/historical_f1_races.csv"

# Check what years already exist in the file
if os.path.exists(output_path):
    existing_df = pd.read_csv(output_path)
    completed_years = existing_df['year'].unique().tolist()
    print(f"📁 Existing data found for seasons: {completed_years}")
else:
    existing_df = pd.DataFrame()
    completed_years = []

target_years = [2022, 2023, 2024, 2025, 2026]
years_to_download = [y for y in target_years if y not in completed_years]

if not years_to_download:
    print("✅ All target seasons (2022-2026) are already downloaded!")
    exit()

print(f"🏎️ Downloading missing seasons: {years_to_download}...")

new_race_data = []

for year in years_to_download:
    print(f"\n================ Season {year} ================")
    try:
        schedule = fastf1.get_event_schedule(year)
    except Exception as err:
        print(f"⚠️ Schedule unavailable for {year}: {err}")
        continue

    for _, event in schedule.iterrows():
        round_num = event['RoundNumber']
        event_name = event['EventName']
        location = event['Location']

        if round_num == 0:
            continue

        try:
            session = fastf1.get_session(year, round_num, 'R')
            # Fast download: skips heavy telemetry channels
            session.load(telemetry=False, weather=False, messages=False)
            
            results = session.results
            if results is None or results.empty:
                continue

            for _, driver in results.iterrows():
                new_race_data.append({
                    'year': int(year),
                    'round': int(round_num),
                    'race_name': str(event_name),
                    'circuit': str(location),
                    'driver_code': str(driver.get('Abbreviation', '')),
                    'driver_name': str(driver.get('FullName', '')),
                    'team': str(driver.get('TeamName', '')),
                    'grid': driver.get('GridPosition', 20),
                    'finish_position': driver.get('ClassifiedPosition', 20),
                    'points': driver.get('Points', 0),
                    'status': str(driver.get('Status', ''))
                })

            print(f"✓ Downloaded: {year} R{round_num:02d} | {event_name}")
        except Exception:
            continue

# Combine existing and new data
if new_race_data:
    new_df = pd.DataFrame(new_race_data)
    final_df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    final_df = existing_df

final_df.to_csv(output_path, index=False)
print(f"\n✅ All done! Total race records in '{output_path}': {len(final_df)}")
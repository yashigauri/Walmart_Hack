# scripts/generate_dataset.py

import pandas as pd
import numpy as np
import itertools
import uuid
import os

ZONES = ['ZoneA', 'ZoneB', 'ZoneC', 'ZoneD']
TIME_SLOTS = ['Morning', 'Afternoon', 'Evening', 'Night']
TRAFFIC_LEVELS = ['Low', 'Medium', 'High']
WEATHER_CONDITIONS = ['Clear', 'Rainy', 'Foggy']
WEIGHT_BINS = [1, 5, 10, 15, 20]  # kg
DISTANCE_BINS = [2, 10, 20, 30, 40, 50]  # km
REPEATS = 3  # simulate multiple deliveries for each combo
OUTPUT_PATH = "data/smart_combination_dataset.csv"

def generate_dataset():
    combinations = list(itertools.product(
        ZONES, ZONES, TIME_SLOTS, TRAFFIC_LEVELS, WEATHER_CONDITIONS, WEIGHT_BINS, DISTANCE_BINS
    ))
    combinations = [c for c in combinations if c[0] != c[1]]

    records = []
    for _ in range(REPEATS):
        for combo in combinations:
            from_zone, to_zone, time_slot, traffic, weather, weight_kg, distance_km = combo

            base_time = distance_km * 2
            traffic_factor = {'Low': 0.9, 'Medium': 1.0, 'High': 1.3}[traffic]
            weather_factor = {'Clear': 1.0, 'Rainy': 1.2, 'Foggy': 1.3}[weather]
            weight_factor = 1 + (weight_kg / 100)
            noise = np.random.normal(loc=1.0, scale=0.08)

            delay_time = round(base_time * traffic_factor * weather_factor * weight_factor * noise, 2)

            records.append({
                'delivery_id': str(uuid.uuid4())[:8],
                'from_zone': from_zone,
                'to_zone': to_zone,
                'time_slot': time_slot,
                'traffic': traffic,
                'weather': weather,
                'weight_kg': weight_kg,
                'distance_km': distance_km,
                'actual_time_min': delay_time
            })

    df = pd.DataFrame(records)
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Generated {len(df)} rows → saved to '{OUTPUT_PATH}'")

if __name__ == "__main__":
    generate_dataset()

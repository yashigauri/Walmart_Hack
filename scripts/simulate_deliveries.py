# scripts/simulate_deliveries.py

import pandas as pd
import numpy as np
import random
import uuid
import os

ZONES = ['ZoneA', 'ZoneB', 'ZoneC', 'ZoneD']
TIME_SLOTS = ['Morning', 'Afternoon', 'Evening', 'Night']
TRAFFIC_LEVELS = ['Low', 'Medium', 'High']
WEATHER_CONDITIONS = ['Clear', 'Rainy', 'Foggy']
OUTPUT_PATH = "data/simulated_test_data.csv"

def simulate_deliveries(n=300):
    simulated_data = []

    for _ in range(n):
        from_zone, to_zone = random.sample(ZONES, 2)
        time_slot = random.choices(TIME_SLOTS, weights=[1, 2, 3, 1])[0]
        traffic = random.choices(TRAFFIC_LEVELS, weights=[1, 2, 3])[0]
        weather = random.choices(WEATHER_CONDITIONS, weights=[3, 2, 1])[0]

        weight_kg = round(random.uniform(0.8, 25.0), 2)
        distance_km = round(random.uniform(3.0, 60.0), 2)

        base_time = distance_km * 2
        traffic_factor = {'Low': 0.9, 'Medium': 1.0, 'High': 1.3}[traffic]
        weather_factor = {'Clear': 1.0, 'Rainy': 1.2, 'Foggy': 1.3}[weather]
        weight_factor = 1 + (weight_kg / 100)
        noise = np.random.normal(loc=1.0, scale=0.08)

        actual_time_min = round(base_time * traffic_factor * weather_factor * weight_factor * noise, 2)

        simulated_data.append({
            'delivery_id': str(uuid.uuid4())[:8],
            'from_zone': from_zone,
            'to_zone': to_zone,
            'time_slot': time_slot,
            'traffic': traffic,
            'weather': weather,
            'weight_kg': weight_kg,
            'distance_km': distance_km,
            'actual_time_min': actual_time_min
        })

    df_sim = pd.DataFrame(simulated_data)
    os.makedirs("data", exist_ok=True)
    df_sim.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Simulated {n} deliveries → saved to '{OUTPUT_PATH}'")

if __name__ == "__main__":
    simulate_deliveries()

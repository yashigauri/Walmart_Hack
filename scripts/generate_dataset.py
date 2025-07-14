from datasets import load_dataset
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
import os


def enrich_datetime(time_str):
    try:
        if pd.isna(time_str):
            return pd.NaT
        return pd.to_datetime(f"2018-{time_str}", format="%Y-%m-%d %H:%M:%S", errors="coerce")
    except Exception:
        return pd.NaT

def haversine(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).km

def get_time_slot(hour):
    if 6 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 18:
        return "Afternoon"
    elif 18 <= hour < 22:
        return "Evening"
    else:
        return "Night"

print("📥 Downloading LaDe-D from Hugging Face...")
ds = load_dataset("Cainiao-AI/LaDe-D", split="delivery_sh")
df = ds.to_pandas()
print("✅ Loaded with shape:", df.shape)
df = ds.to_pandas()
print("✅ Loaded with shape:", df.shape)
print("📌 Available columns:", df.columns.tolist())

# Fix datetime parsing for known time fields
datetime_fields = ['accept_time', 'accept_gps_time', 'delivery_time', 'delivery_gps_time']

for col in datetime_fields:
    if col in df.columns:
        df[col] = df[col].apply(enrich_datetime)
print("⚙ Processing features...")

df = df.dropna(subset=['accept_time', 'delivery_time',
                       'accept_gps_lat', 'accept_gps_lng',
                       'delivery_gps_lat', 'delivery_gps_lng'])

df['accept_time'] = pd.to_datetime(df['accept_time'])
df['delivery_time'] = pd.to_datetime(df['delivery_time'])

df['actual_time_min'] = (df['delivery_time'] - df['accept_time']).dt.total_seconds() / 60
df['distance_km'] = df.apply(lambda row: haversine(
    row['accept_gps_lat'], row['accept_gps_lng'],
    row['delivery_gps_lat'], row['delivery_gps_lng']), axis=1)

df['time_slot'] = df['accept_time'].dt.hour.apply(get_time_slot)
df['from_zone'] = df['aoi_id']
df['to_zone'] = df['region_id']

df['weight_kg'] = 5.0  # Dummy constant

# Final structure
df_cleaned = df[['order_id', 'from_zone', 'to_zone', 'time_slot',
                  'weight_kg', 'distance_km', 'actual_time_min']]
df_cleaned = df_cleaned.rename(columns={'order_id': 'delivery_id'})

os.makedirs("data", exist_ok=True)
df_cleaned.to_csv("data/lade_delivery_cleaned.csv", index=False)
print("✅ Cleaned file saved to data/lade_delivery_cleaned.csv")
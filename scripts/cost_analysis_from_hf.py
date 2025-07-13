from datasets import load_dataset
import pandas as pd
import numpy as np
import os
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# === Configurable cost parameters ===
BASE_COST = 10
PER_KM_RATE = 5
PER_MIN_RATE = 1

def haversine(lon1, lat1, lon2, lat2):
    R = 6371
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

print("📥 Downloading LaDe-D from Hugging Face...")
ds = load_dataset("Cainiao-AI/LaDe-D", split="delivery_sh")
df = ds.to_pandas()
print("✅ Loaded with shape:", df.shape)

# === Diagnostic: check what's in the columns ===


# Step 1: Build full datetime using ds
def enrich_datetime(time_str):
    try:
        if pd.isna(time_str):
            return pd.NaT
        
        return pd.to_datetime(f"2018-{time_str}", format="%Y-%m-%d %H:%M:%S", errors="coerce")
    except Exception:
        return pd.NaT


df['accept_time'] = df['accept_time'].apply(enrich_datetime)
df['delivery_time'] = df['delivery_time'].apply(enrich_datetime)
print(df[['accept_time', 'delivery_time']].dropna().head(5))


print("🧪 Sample enriched accept_time:", df['accept_time'].dropna().astype(str).head().tolist())
print("🧪 Sample enriched delivery_time:", df['delivery_time'].dropna().astype(str).head().tolist())

# Step 2: Filter valid rows
print("📦 Before filtering:", len(df))
df = df.dropna(subset=[
    'accept_time', 'delivery_time',
    'accept_gps_lng', 'accept_gps_lat',
    'delivery_gps_lng', 'delivery_gps_lat'
])
print("📉 After dropping invalids:", len(df))

# Step 3: Compute duration
df['delivery_duration_min'] = (df['delivery_time'] - df['accept_time']).dt.total_seconds() / 60
df = df[df['delivery_duration_min'] > 0]
print("⏱️ Positive durations:", len(df))

# Step 4: Distance & Cost
df['delivery_distance_km'] = df.apply(
    lambda row: haversine(row['accept_gps_lng'], row['accept_gps_lat'],
                          row['delivery_gps_lng'], row['delivery_gps_lat']), axis=1
)
df['delivery_cost'] = BASE_COST + df['delivery_distance_km'] * PER_KM_RATE + df['delivery_duration_min'] * PER_MIN_RATE

# Step 5: Save
os.makedirs("outputs", exist_ok=True)
df.to_csv("outputs/lade_costs.csv", index=False)
print("✅ Output saved to outputs/lade_costs.csv")

# Step 6: Summary
print("\n📊 Cost Summary:")
print(f"Average Cost: ₹ {df['delivery_cost'].mean():.2f}")
print("Top 5 Expensive Deliveries:")
print(df[['order_id', 'delivery_cost', 'delivery_distance_km', 'delivery_duration_min']]
      .sort_values(by='delivery_cost', ascending=False).head())


# === Step 7: Anomaly Detection ===
print("\n🚨 Detecting anomalies...")

def detect_anomalies(series, label, k=1.5):
    Q1 = series.quantile(0.25)
    Q3 = series.quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - k * IQR
    upper = Q3 + k * IQR
    outliers = df[(series < lower) | (series > upper)]
    print(f"{label}: Found {len(outliers)} anomalies (IQR method)")
    return outliers

cost_outliers = detect_anomalies(df['delivery_cost'], "💰 Cost Anomalies")
duration_outliers = detect_anomalies(df['delivery_duration_min'], "⏱️ Duration Anomalies")
distance_outliers = detect_anomalies(df['delivery_distance_km'], "📏 Distance Anomalies")

# Save anomalies for review
os.makedirs("outputs/anomalies", exist_ok=True)
cost_outliers.to_csv("outputs/anomalies/cost_outliers.csv", index=False)
duration_outliers.to_csv("outputs/anomalies/duration_outliers.csv", index=False)
distance_outliers.to_csv("outputs/anomalies/distance_outliers.csv", index=False)

print("✅ Anomaly reports saved in outputs/anomalies/")

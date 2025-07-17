import pandas as pd
import numpy as np
import os

# === Configurable cost parameters ===
BASE_COST = 10
PER_KM_RATE = 5
PER_MIN_RATE = 1

# Step 1: Load preprocessed cleaned dataset
df = pd.read_csv("data/lade_delivery_enhanced.csv")
print("✅ Loaded enhanced dataset:", df.shape)

# Step 2: Rename columns to match downstream logic
df['delivery_duration_min'] = df['actual_time_min']
df['delivery_distance_km'] = df['distance_km']

# Step 3: Compute cost
df['delivery_cost'] = BASE_COST + df['delivery_distance_km'] * PER_KM_RATE + df['delivery_duration_min'] * PER_MIN_RATE

# Step 4: Save to outputs
os.makedirs("outputs", exist_ok=True)
df.to_csv("outputs/lade_costs.csv", index=False)
print("✅ Output saved to outputs/lade_costs.csv")

# Step 5: Summary
print("\n📊 Cost Summary:")
print(f"Average Cost: ₹ {df['delivery_cost'].mean():.2f}")
print("Top 5 Expensive Deliveries:")
print(df[['delivery_id', 'delivery_cost', 'delivery_distance_km', 'delivery_duration_min']]
      .sort_values(by='delivery_cost', ascending=False).head())

# === Step 6: Anomaly Detection ===
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

# Save anomaly reports
os.makedirs("outputs/anomalies", exist_ok=True)
cost_outliers.to_csv("outputs/anomalies/cost_outliers.csv", index=False)
duration_outliers.to_csv("outputs/anomalies/duration_outliers.csv", index=False)
distance_outliers.to_csv("outputs/anomalies/distance_outliers.csv", index=False)
print("✅ Anomaly reports saved in outputs/anomalies/")

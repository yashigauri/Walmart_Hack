# scripts/supplier_score_engine.py

import pandas as pd
import numpy as np
import os

# === Load your predictions CSV ===
print("📥 Loading predictions data...")
df = pd.read_csv("outputs/predictions_full_report.csv")

# For demonstration, assume there is a 'supplier' column.
# If you don't have one, create a dummy column based on zones for more realistic mapping:
if "supplier" not in df.columns:
    print("⚠️ No supplier column found. Creating zone-based suppliers for realistic mapping...")
    # Create more realistic supplier mapping based on from_zone
    zone_to_supplier = {
        "ZoneA": ["Supplier_Alpha", "Supplier_Beta"],
        "ZoneB": ["Supplier_Gamma", "Supplier_Delta"], 
        "ZoneC": ["Supplier_Epsilon", "Supplier_Zeta"]
    }
    
    def assign_supplier(row):
        suppliers = zone_to_supplier.get(row["from_zone"], ["Unknown_Supplier"])
        return np.random.choice(suppliers)
    
    df["supplier"] = df.apply(assign_supplier, axis=1)

# === Enhanced KPI Computation ===
print("📊 Computing enhanced KPIs per supplier...")

# Compute on-time rate (exact matches only)
on_time_rate = (
    df[df["predicted_delay_label"] == "On Time"]
    .groupby("supplier")["delivery_id"]
    .count()
    / df.groupby("supplier")["delivery_id"].count()
)

# Compute delay severity rate (Very Delayed is worse than Delayed)
severe_delay_rate = (
    df[df["predicted_delay_label"] == "Very Delayed"]
    .groupby("supplier")["delivery_id"]
    .count()
    / df.groupby("supplier")["delivery_id"].count()
)

# Weather resilience score (performance in adverse conditions)
weather_performance = df[df["weather"].isin(["Rainy", "Foggy"])].groupby("supplier").apply(
    lambda x: (x["predicted_delay_label"] == "On Time").sum() / len(x) if len(x) > 0 else 0
).fillna(0)

# Distance efficiency (actual vs predicted time ratio)
df["efficiency_ratio"] = df["actual_time_min"] / df["predicted_time_min"]
distance_efficiency = df.groupby("supplier")["efficiency_ratio"].mean()

# RL optimization acceptance rate (how often RL suggestions help)
rl_acceptance = df[df["rl_action"] != "Continue"].groupby("supplier").size() / df.groupby("supplier").size()

# Core aggregations
kpi_table = df.groupby("supplier").agg(
    avg_predicted_delay=("predicted_time_min", "mean"),
    avg_actual_delay=("actual_time_min", "mean"),
    total_rl_time_saved=("rl_estimated_delay", lambda x: (df.loc[x.index, "predicted_time_min"] - x).sum()),
    order_volume=("delivery_id", "count"),
    avg_distance=("distance_km", "mean"),
    avg_weight=("weight_kg", "mean"),
    high_traffic_deliveries=("traffic", lambda x: (x == "High").sum()),
    zones_served=("from_zone", "nunique")
).reset_index()

# Merge additional KPIs
kpi_table["on_time_rate"] = kpi_table["supplier"].map(on_time_rate).fillna(0)
kpi_table["severe_delay_rate"] = kpi_table["supplier"].map(severe_delay_rate).fillna(0)
kpi_table["weather_resilience"] = kpi_table["supplier"].map(weather_performance).fillna(0)
kpi_table["distance_efficiency"] = kpi_table["supplier"].map(distance_efficiency).fillna(1.0)
kpi_table["rl_optimization_rate"] = kpi_table["supplier"].map(rl_acceptance).fillna(0)

# === Enhanced Normalizations ===
print("⚙️ Computing normalized metrics...")

# Normalize metrics (0-1 scale)
def safe_normalize(series, reverse=False):
    """Safely normalize series to 0-1 range, handling edge cases"""
    if series.max() == series.min():
        return pd.Series([0.5] * len(series), index=series.index)
    
    normalized = (series - series.min()) / (series.max() - series.min())
    return (1 - normalized) if reverse else normalized

# Higher values are worse (reverse normalization)
kpi_table["norm_avg_delay"] = safe_normalize(kpi_table["avg_predicted_delay"], reverse=True)
kpi_table["norm_severe_delay"] = safe_normalize(kpi_table["severe_delay_rate"], reverse=True)
kpi_table["norm_efficiency"] = safe_normalize(kpi_table["distance_efficiency"], reverse=True)

# Higher values are better (normal normalization)
kpi_table["norm_on_time"] = safe_normalize(kpi_table["on_time_rate"])
kpi_table["norm_weather_resilience"] = safe_normalize(kpi_table["weather_resilience"])
kpi_table["norm_rl_optimization"] = safe_normalize(kpi_table["rl_optimization_rate"])

# Volume-based reliability score
kpi_table["reliability_score"] = (
    kpi_table["on_time_rate"] * 0.6 + 
    kpi_table["weather_resilience"] * 0.4
) * np.log1p(kpi_table["order_volume"]) / np.log1p(kpi_table["order_volume"].max())

# === Enhanced Weighted Score ===
print("🎯 Computing comprehensive supplier scores...")

kpi_table["score"] = (
    0.35 * kpi_table["norm_on_time"]           # Primary: On-time performance
    + 0.20 * kpi_table["norm_avg_delay"]       # Delay management
    + 0.15 * kpi_table["norm_severe_delay"]    # Severe delay avoidance
    + 0.10 * kpi_table["norm_weather_resilience"] # Weather resilience
    + 0.10 * kpi_table["norm_efficiency"]      # Distance efficiency
    + 0.05 * kpi_table["norm_rl_optimization"] # AI optimization acceptance
    + 0.05 * safe_normalize(kpi_table["reliability_score"]) # Volume-adjusted reliability
)

# === Walmart-Aligned Tier System ===
def assign_tier(row):
    """Assign tiers based on Walmart-like performance standards"""
    score = row["score"]
    on_time = row["on_time_rate"]
    
    # Walmart expects >95% on-time, but adjust for realistic current performance
    if score > 0.80 and on_time > 0.30:  # Top performers
        return "Gold ⭐"
    elif score > 0.65 and on_time > 0.20:  # Good performers
        return "Silver 🥈"
    elif score > 0.50 and on_time > 0.15:  # Acceptable performers
        return "Bronze 🥉"
    elif score > 0.35:  # Needs improvement
        return "Development 📈"
    else:  # Critical issues
        return "Critical Review ⚠️"

kpi_table["tier"] = kpi_table.apply(assign_tier, axis=1)

# === Risk Assessment ===
kpi_table["risk_level"] = pd.cut(
    kpi_table["score"],
    bins=[0, 0.3, 0.5, 0.7, 1.0],
    labels=["High Risk", "Medium Risk", "Low Risk", "Preferred"]
)

# === Business Impact Metrics ===
kpi_table["potential_time_savings"] = kpi_table["total_rl_time_saved"]
kpi_table["business_impact"] = (
    kpi_table["score"] * kpi_table["order_volume"] * kpi_table["avg_distance"]
).round(2)

# === Sort by performance ===
kpi_table = kpi_table.sort_values("score", ascending=False)

# === Save Results ===
os.makedirs("outputs", exist_ok=True)
output_path = "outputs/supplier_scores.csv"
kpi_table.to_csv(output_path, index=False)

print("✅ Enhanced supplier scores saved to:", output_path)
print("\n🏆 SUPPLIER PERFORMANCE DASHBOARD")
print("=" * 50)
print(kpi_table[["supplier", "tier", "score", "on_time_rate", "order_volume", "risk_level"]].to_string(index=False))

print(f"\n📊 SUMMARY STATISTICS:")
print(f"Total Suppliers: {len(kpi_table)}")
print(f"Average On-Time Rate: {kpi_table['on_time_rate'].mean():.1%}")
print(f"Gold Tier Suppliers: {(kpi_table['tier'] == 'Gold ⭐').sum()}")
print(f"Critical Review: {(kpi_table['tier'] == 'Critical Review ⚠️').sum()}")
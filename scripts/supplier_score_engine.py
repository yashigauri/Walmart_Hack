# scripts/supplier_score_engine.py
# ----------------------------------------------------------------------
# Builds supplier–level KPIs from outputs/predictions_full_report.csv
# • Works whether predicted_delay_label is numeric (0/1/2) or strings.
# • Handles optional columns: weather, traffic, rl_action, rl_estimated_delay.
# ----------------------------------------------------------------------

import pandas as pd
import numpy as np
import os

PRED_CSV  = "outputs/predictions_full_report.csv"
OUT_CSV   = "outputs/supplier_scores.csv"

print("📥 Loading predictions data …")
df = pd.read_csv(PRED_CSV)
print(f"   Rows loaded: {len(df):,}")

# ────────────────────────────────────────────────────────────────────
# 1️⃣  Ensure supplier column
# --------------------------------------------------------------------
if "supplier" not in df.columns:
    print("⚠️  No supplier column found – creating synthetic suppliers from from_zone")

    def zone_to_supplier(zone_id: int) -> str:
        if zone_id < 200:
            return np.random.choice(["Supplier_Alpha", "Supplier_Beta"])
        elif zone_id < 400:
            return np.random.choice(["Supplier_Gamma", "Supplier_Delta"])
        else:
            return np.random.choice(["Supplier_Epsilon", "Supplier_Zeta"])

    df["supplier"] = df["from_zone"].apply(zone_to_supplier)

# ────────────────────────────────────────────────────────────────────
# 2️⃣  Make sure predicted_delay_label is in string form
# --------------------------------------------------------------------
delay_map = {0: "On Time", 1: "Delayed", 2: "Very Delayed"}

if pd.api.types.is_numeric_dtype(df["predicted_delay_label"]):
    df["predicted_delay_label"] = df["predicted_delay_label"].map(delay_map)
    print("ℹ️  Converted numeric labels → string labels")
else:
    # Standardise capitalisation / spacing just in case
    df["predicted_delay_label"] = df["predicted_delay_label"].str.strip().str.title()

# Quick sanity
print("\nLabel distribution after mapping:")
print(df["predicted_delay_label"].value_counts(dropna=False))

# ────────────────────────────────────────────────────────────────────
# 3️⃣  KPI calculations
# --------------------------------------------------------------------
print("\n📊 Computing KPIs per supplier …")

on_time_rate = (
    df[df["predicted_delay_label"] == "On Time"]
    .groupby("supplier")["delivery_id"].count()
    / df.groupby("supplier")["delivery_id"].count()
)

severe_delay_rate = (
    df[df["predicted_delay_label"] == "Very Delayed"]
    .groupby("supplier")["delivery_id"].count()
    / df.groupby("supplier")["delivery_id"].count()
)

# Weather resilience (only if weather column exists)
if "weather" in df.columns:
    weather_resilience = (
        df[df["weather"].isin(["Rainy", "Foggy"])]
        .groupby("supplier")
        .apply(lambda x: (x["predicted_delay_label"] == "On Time").mean())
    )
else:
    weather_resilience = pd.Series(dtype=float)

# Efficiency ratio (actual / predicted)
df["efficiency_ratio"] = df["actual_time_min"] / df["predicted_time_min"]
distance_efficiency = df.groupby("supplier")["efficiency_ratio"].mean()

# RL optimisation acceptance rate (if rl_action exists)
if "rl_action" in df.columns:
    rl_acceptance = (
        df[df["rl_action"] != "Continue"].groupby("supplier").size()
        / df.groupby("supplier").size()
    )
else:
    rl_acceptance = pd.Series(dtype=float)

# Total RL time saved (if rl_estimated_delay exists)
if "rl_estimated_delay" in df.columns:
    rl_savings = (
        df.groupby("supplier")
        .apply(lambda g: (g["predicted_time_min"] - g["rl_estimated_delay"]).sum())
    )
else:
    rl_savings = pd.Series(0, index=df["supplier"].unique())

# Main aggregated table
kpi = df.groupby("supplier").agg(
    avg_predicted_delay=("predicted_time_min", "mean"),
    avg_actual_delay=("actual_time_min", "mean"),
    order_volume=("delivery_id", "count"),
    avg_distance=("distance_km", "mean"),
    avg_weight=("weight_kg", "mean"),
    zones_served=("from_zone", "nunique"),
).reset_index()

# Add optional traffic metric
if "traffic" in df.columns:
    high_traffic = df[df["traffic"] == "High"].groupby("supplier").size()
    kpi["high_traffic_deliveries"] = kpi["supplier"].map(high_traffic).fillna(0)
else:
    kpi["high_traffic_deliveries"] = 0

# Merge calculated KPIs
kpi["on_time_rate"]         = kpi["supplier"].map(on_time_rate)        .fillna(0)
kpi["severe_delay_rate"]    = kpi["supplier"].map(severe_delay_rate)   .fillna(0)
kpi["weather_resilience"]   = kpi["supplier"].map(weather_resilience)  .fillna(0)
kpi["distance_efficiency"]  = kpi["supplier"].map(distance_efficiency) .fillna(1.0)
kpi["rl_optimization_rate"] = kpi["supplier"].map(rl_acceptance)       .fillna(0)
kpi["total_rl_time_saved"]  = kpi["supplier"].map(rl_savings)          .fillna(0)

# ────────────────────────────────────────────────────────────────────
# 4️⃣  Normalisation helpers
# --------------------------------------------------------------------
def safe_normalize(series: pd.Series, reverse: bool = False) -> pd.Series:
    if series.max() == series.min():
        return pd.Series(0.5, index=series.index)
    norm = (series - series.min()) / (series.max() - series.min())
    return 1 - norm if reverse else norm

# Normalised fields
kpi["norm_on_time"]           = safe_normalize(kpi["on_time_rate"])
kpi["norm_avg_delay"]         = safe_normalize(kpi["avg_predicted_delay"], reverse=True)
kpi["norm_severe_delay"]      = safe_normalize(kpi["severe_delay_rate"], reverse=True)
kpi["norm_efficiency"]        = safe_normalize(kpi["distance_efficiency"], reverse=True)
kpi["norm_weather_resilience"]= safe_normalize(kpi["weather_resilience"])
kpi["norm_rl_optimization"]   = safe_normalize(kpi["rl_optimization_rate"])

# Reliability score (volume‑weighted)
kpi["reliability_score"] = (
    kpi["on_time_rate"] * 0.6 + kpi["weather_resilience"] * 0.4
) * np.log1p(kpi["order_volume"]) / np.log1p(kpi["order_volume"].max())

# ────────────────────────────────────────────────────────────────────
# 5️⃣  Composite supplier score & tiers
# --------------------------------------------------------------------
kpi["score"] = (
    0.35 * kpi["norm_on_time"]
  + 0.20 * kpi["norm_avg_delay"]
  + 0.15 * kpi["norm_severe_delay"]
  + 0.10 * kpi["norm_weather_resilience"]
  + 0.10 * kpi["norm_efficiency"]
  + 0.05 * kpi["norm_rl_optimization"]
  + 0.05 * safe_normalize(kpi["reliability_score"])
)

def assign_tier(row):
    s, r = row["score"], row["on_time_rate"]
    if s > 0.80 and r > 0.30:
        return "Gold ⭐"
    if s > 0.65 and r > 0.20:
        return "Silver 🥈"
    if s > 0.50 and r > 0.15:
        return "Bronze 🥉"
    if s > 0.35:
        return "Development 📈"
    return "Critical Review ⚠️"

kpi["tier"] = kpi.apply(assign_tier, axis=1)

# Risk level buckets
kpi["risk_level"] = pd.cut(
    kpi["score"],
    bins=[0, 0.3, 0.5, 0.7, 1.0],
    labels=["High Risk", "Medium Risk", "Low Risk", "Preferred"]
)

# Extra business impact metrics
kpi["potential_time_savings"] = kpi["total_rl_time_saved"]
kpi["business_impact"] = (
    kpi["score"] * kpi["order_volume"] * kpi["avg_distance"]
).round(2)

# ────────────────────────────────────────────────────────────────────
# 6️⃣  Save results & dashboard printout
# --------------------------------------------------------------------
kpi_sorted = kpi.sort_values("score", ascending=False)
os.makedirs("outputs", exist_ok=True)
kpi_sorted.to_csv(OUT_CSV, index=False)

print(f"\n✅ Supplier scores saved → {OUT_CSV}")
print("\n🏆 SUPPLIER PERFORMANCE DASHBOARD")
print("=" * 50)
print(
    kpi_sorted[
        ["supplier", "tier", "score", "on_time_rate",
         "order_volume", "risk_level"]
    ].to_string(index=False)
)

print("\n📊 SUMMARY STATISTICS")
print(f"Total suppliers: {len(kpi_sorted)}")
print(f"Avg on‑time rate: {kpi_sorted['on_time_rate'].mean():.1%}")
print(f"Gold tier suppliers: {(kpi_sorted['tier']=='Gold ⭐').sum()}")
print(f"Critical review: {(kpi_sorted['tier']=='Critical Review ⚠️').sum()}")

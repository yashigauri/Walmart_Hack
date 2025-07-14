import pandas as pd
import numpy as np
import joblib
import os
from scripts.rl_agent.agent_runner import get_rl_optimal_reroute
from scripts.heatmap_generator import generate_all_heatmaps

# Paths
INPUT_FILE = "data/lade_delivery_enhanced.csv"
CLF_PATH = "models/delay_classifier.pkl"
REG_PATH = "models/duration_regressor.pkl"
OUTPUT_PATH = "outputs/predictions_full_report.csv"

# Features used during training
FEATURE_COLS = [
    "distance_km", "weight_kg", "same_zone", "weight_per_km",
    "time_slot_Morning", "time_slot_Night",
    "weight_category_light", "weight_category_medium",
    "weight_category_heavy", "weight_category_very_heavy",
    "distance_category_short", "distance_category_medium",
    "distance_category_long", "distance_category_very_long"
]

def main():
    print("📥 Loading enhanced dataset...")
    df = pd.read_csv(INPUT_FILE)
    print(f"   {len(df):,} rows")

    # Drop anomalies — just like in training
    df = df[df["is_anomaly"] == 0].reset_index(drop=True)

    # Ensure all training-time features exist
    for col in FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0

    X = df[FEATURE_COLS]

    print("🔧 Loading models...")
    clf = joblib.load(CLF_PATH)
    reg = joblib.load(REG_PATH)

    print("🔮 Making predictions...")
    df["predicted_delay_label"] = clf.predict(X)
    df["predicted_time_min"] = np.expm1(reg.predict(X))

    # Map numeric labels to readable classes
    label_map = {0: "On Time", 1: "Delayed", 2: "Very Delayed"}
    df["predicted_delay_label"] = df["predicted_delay_label"].map(label_map)

    # ── RL Agent Integration ──────────────────────────────────────────────
    print("🤖 Running RL rerouting agent...")
    reroutes = []
    for idx, row in df.iterrows():
        suggestion = get_rl_optimal_reroute(row)
        reroutes.append(suggestion)
    reroute_df = pd.DataFrame(reroutes)
    final_df = pd.concat([df, reroute_df], axis=1)

    # Save predictions
    os.makedirs("outputs", exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Predictions saved → {OUTPUT_PATH}")

    # Generate all heatmaps
    print("🎨 Generating heatmaps …")
    try:
        generate_all_heatmaps(final_df, output_dir="outputs/")
    except Exception as e:
        print("⚠️ Heatmap generation failed:", e)

    # Summary
    print("\n📊 SUMMARY:")
    print(f"Total predictions: {len(final_df)}")
    print("Delay distribution:")
    print(final_df["predicted_delay_label"].value_counts())

    if "actual_time_min" in final_df.columns:
        mae = np.mean(np.abs(final_df["actual_time_min"] - final_df["predicted_time_min"]))
        print(f"Mean Absolute Error: {mae:.2f} min")

    if "suggested_route" in final_df.columns:
        print("Top route suggestions:")
        print(final_df["suggested_route"].value_counts().head())

if __name__ == "__main__":
    main()

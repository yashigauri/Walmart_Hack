# scripts/feature_engineering.py

import os
import logging
from typing import Tuple
import numpy as np
import pandas as pd

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────
INPUT_PATH  = "data/lade_delivery_cleaned.csv"
OUTPUT_PATH = "data/lade_delivery_enhanced.csv"

# ── 1. Load ────────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    if not os.path.exists(INPUT_PATH):
        raise FileNotFoundError(f"{INPUT_PATH} not found.")
    df = pd.read_csv(INPUT_PATH)
    logger.info("Loaded %d rows × %d columns", *df.shape)
    return df

# ── 2. Feature Engineering ────────────────────────────────────────────────
def add_features(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Adding engineered features...")

    # Safe, interpretable features only — no target leakage
    df["weight_per_km"] = np.where(
        df["distance_km"] > 0,
        df["weight_kg"] / df["distance_km"],
        0,
    )

    df["weight_category"] = pd.cut(
        df["weight_kg"],
        bins=[0, 50, 200, 400, 600, float("inf")],
        labels=["very_light", "light", "medium", "heavy", "very_heavy"]
    ).astype(str)

    df["distance_category"] = pd.cut(
        df["distance_km"],
        bins=[0, 2, 5, 10, 20, float("inf")],
        labels=["very_short", "short", "medium", "long", "very_long"]
    ).astype(str)

    df["same_zone"] = (df["from_zone"] == df["to_zone"]).astype(np.int8)
    df["zone_pair"] = df["from_zone"].astype(str) + "-" + df["to_zone"].astype(str)

    df["delay_label"] = (df["actual_time_min"] > 90).astype(np.int8)
    df["severe_delay_label"] = (df["actual_time_min"] > 180).astype(np.int8)

    logger.info("Feature set expanded to %d columns.", df.shape[1])
    return df

# ── 3. Anomaly Detection ───────────────────────────────────────────────────
def _iqr_flag(series: pd.Series, k: float = 1.5) -> pd.Series:
    q1, q3 = series.quantile([0.25, 0.75])
    iqr = q3 - q1
    return ((series < q1 - k * iqr) | (series > q3 + k * iqr)).astype(np.int8)

def detect_anomalies(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Detecting anomalies...")
    df["time_anomaly"]   = _iqr_flag(df["actual_time_min"])
    df["dist_anomaly"]   = _iqr_flag(df["distance_km"])
    df["weight_anomaly"] = _iqr_flag(df["weight_kg"])
    df["is_anomaly"] = (
        df[["time_anomaly", "dist_anomaly", "weight_anomaly"]].sum(axis=1) > 0
    ).astype(np.int8)
    logger.info("Flagged %d anomalous records.", df["is_anomaly"].sum())
    return df

# ── 4. Optimise Dtypes ─────────────────────────────────────────────────────
def optimise_dtypes(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Optimising dtypes...")
    for col in df.select_dtypes("int64"):
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes("float64"):
        df[col] = pd.to_numeric(df[col], downcast="float")
    for cat in ["weight_category", "distance_category", "time_slot", "zone_pair"]:
        if cat in df.columns:
            df[cat] = df[cat].astype("category")
    return df

# ── 5. Save ────────────────────────────────────────────────────────────────
def save(df: pd.DataFrame) -> None:
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved → %s", OUTPUT_PATH)
    logger.info("Anomaly rate: %.2f %%", 100 * df["is_anomaly"].mean())
    logger.info("Delay   rate: %.2f %%", 100 * df["delay_label"].mean())

def prepare_model_input(raw_input: dict, for_training=False) -> pd.DataFrame:
    if for_training:
        df = pd.DataFrame(raw_input)
    else:
        df = pd.DataFrame([raw_input])

    df.rename(columns={"weight": "weight_kg", "distance": "distance_km"}, inplace=True)

    # Only required feature engineering
    df["weight_per_km"] = np.where(df["distance_km"] > 0, df["weight_kg"] / df["distance_km"], 0)
    df["same_zone"] = (df["from_zone"] == df["to_zone"]).astype(int)
    # Categorize weight manually
    def get_weight_category(weight):
        if weight < 5:
            return "light"
        elif weight < 15:
            return "medium"
        elif weight < 30:
            return "heavy"
        else:
            return "very_heavy"

    df["weight_category"] = df["weight_kg"].apply(get_weight_category)
    def get_distance_category(distance):
        if distance < 5:
            return "short"
        elif distance < 15:
            return "medium"
        elif distance < 30:
            return "long"
        else:
            return "very_long"

    df["distance_category"] = df["distance_km"].apply(get_distance_category)

    # One-hot encoding for time_slot, weight_category, distance_category
    time_dummies = pd.get_dummies(df["time_slot"], prefix="time_slot")
    weight_dummies = pd.get_dummies(df["weight_category"], prefix="weight_category")
    distance_dummies = pd.get_dummies(df["distance_category"], prefix="distance_category")

    df = pd.concat([df, time_dummies, weight_dummies, distance_dummies], axis=1)

    # Ensure all expected features are present (fill missing with 0)
    for col in [
        "time_slot_Morning", "time_slot_Night",
        "weight_category_light", "weight_category_medium",
        "weight_category_heavy", "weight_category_very_heavy",
        "distance_category_short", "distance_category_medium",
        "distance_category_long", "distance_category_very_long"
    ]:
        if col not in df.columns:
            df[col] = 0

    # Final feature selection
    feature_cols = [
        "distance_km", "weight_kg", "same_zone", "weight_per_km",
        "time_slot_Morning", "time_slot_Night",
        "weight_category_light", "weight_category_medium",
        "weight_category_heavy", "weight_category_very_heavy",
        "distance_category_short", "distance_category_medium",
        "distance_category_long", "distance_category_very_long"
    ]

    return df[feature_cols]


# ── 6. Main ────────────────────────────────────────────────────────────────
def main() -> Tuple[str, str]:
    df = load_data()
    df = add_features(df)
    df = detect_anomalies(df)
    df = optimise_dtypes(df)
    save(df)
    return (OUTPUT_PATH, "✅ Feature engineering complete!")

if __name__ == "__main__":
    main()
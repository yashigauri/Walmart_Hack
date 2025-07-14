"""
Evaluate predictions using trained XGBoost classifier + log-target Random-Forest regressor
• Drops anomaly rows                (is_anomaly == 1)
• Uses log-transformed target inversion for regressor
• Outputs classification report, confusion matrix, and MAE
"""

import os
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix,
    mean_absolute_error, balanced_accuracy_score
)

# ── Paths ─────────────────────────────────────────────────────────────
DATA_PATH   = "data/lade_delivery_enhanced.csv"
CLF_PATH    = "models/delay_classifier.pkl"
REG_PATH    = "models/duration_regressor.pkl"
OUT_CSV     = "outputs/predictions_full_report.csv"
CM_PATH     = "outputs/classification_confusion_matrix.png"

print("📁 Loaded enhanced dataset:")
df = pd.read_csv(DATA_PATH)
print(f"   {len(df):,} rows")

# ── Drop anomalies ─────────────────────────────────────────────────────
df = df[df["is_anomaly"] == 0].reset_index(drop=True)

# ── Features ──────────────────────────────────────────────────────────
feature_cols = [
    "distance_km", "weight_kg", "same_zone", "weight_per_km",
    "time_slot_Morning", "time_slot_Night",
    "weight_category_light", "weight_category_medium",
    "weight_category_heavy", "weight_category_very_heavy",
    "distance_category_short", "distance_category_medium",
    "distance_category_long", "distance_category_very_long"
]
for col in feature_cols:
    if col not in df.columns:
        df[col] = 0

X = df[feature_cols]
y_true_class = df["actual_time_min"].apply(
    lambda t: 0 if t <= 40 else 1 if t <= 70 else 2
)
y_true_reg = df["actual_time_min"]

# ── Load models ────────────────────────────────────────────────────────
print("📦 Loading trained models …")
clf = joblib.load(CLF_PATH)
reg = joblib.load(REG_PATH)

# ── Run predictions ────────────────────────────────────────────────────
print("🔮 Running ML predictions …")
y_pred_class = clf.predict(X)

y_pred_reg_log = reg.predict(X)
y_pred_reg = np.expm1(y_pred_reg_log)  # Invert log-transform

# ── Save predictions ───────────────────────────────────────────────────
df["predicted_delay_label"] = y_pred_class
df["predicted_time_min"]    = y_pred_reg
df.to_csv(OUT_CSV, index=False)
print(f"💾 Saved predictions → {OUT_CSV}")

# ── Classification Report ─────────────────────────────────────────────
print("\n🔍 Classification Report:")
print(classification_report(
    y_true_class, y_pred_class, digits=3,
    target_names=["On Time", "Delayed", "Very Delayed"]
))
print("Balanced Accuracy:", balanced_accuracy_score(y_true_class, y_pred_class))

# ── Confusion Matrix ───────────────────────────────────────────────────
cm = confusion_matrix(y_true_class, y_pred_class)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["On Time", "Delayed", "Very Delayed"], yticklabels=["On Time", "Delayed", "Very Delayed"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig(CM_PATH)
print(f"✅ Saved confusion matrix → {CM_PATH}")

# ── Regression Metrics ────────────────────────────────────────────────
mae = mean_absolute_error(y_true_reg, y_pred_reg)
print(f"\n🕒 MAE (duration regressor): {mae:.2f} min")

print("\n✅ Evaluation complete.")


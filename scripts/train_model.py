"""
Train a 3‑class XGBoost delay classifier + Random‑Forest duration regressor
• Drops anomaly rows                (is_anomaly == 1)
• Uses log‑transformed target (ln(1+minutes)) for the regressor
Compatible with data/lade_delivery_enhanced.csv.
"""

import os, time, joblib, numpy as np, pandas as pd
from math import sqrt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    classification_report, balanced_accuracy_score,
    mean_absolute_error, mean_squared_error,
)
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from xgboost import XGBClassifier

# ── Paths ────────────────────────────────────────────────────────────────
INPUT_CSV = "data/lade_delivery_enhanced.csv"
CLF_PATH  = "models/delay_classifier.pkl"
REG_PATH  = "models/duration_regressor.pkl"

os.makedirs("models", exist_ok=True)
os.makedirs("outputs", exist_ok=True)

print("🚀  Training pipeline started")
t0 = time.time()

# ── 1. Load & clean dataset ──────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV)
print(f"📁  Loaded {len(df):,} rows before cleaning")

# Drop anomalous rows
orig_rows = len(df)
df = df[df["is_anomaly"] == 0].reset_index(drop=True)
print(f"🧹  Removed anomalies: {orig_rows - len(df):,} rows → {len(df):,} remain")

# ── 2. Build multiclass delay label ──────────────────────────────────────
def classify_delay(t):
    return 0 if t <= 40 else 1 if t <= 70 else 2

df["delay_label"] = df["actual_time_min"].apply(classify_delay)
print("🔢  Class distribution:")
print(df["delay_label"].value_counts().sort_index())

# ── 3. Feature matrix (same engineered cols) ─────────────────────────────
feature_cols = [
    "distance_km", "weight_kg", "same_zone", "weight_per_km",
    "time_slot_Morning", "time_slot_Night",
    "weight_category_light", "weight_category_medium",
    "weight_category_heavy", "weight_category_very_heavy",
    "distance_category_short", "distance_category_medium",
    "distance_category_long", "distance_category_very_long"
]
for col in feature_cols:       # ensure all one‑hot cols exist
    if col not in df.columns:
        df[col] = 0

X       = df[feature_cols]
y_class = df["delay_label"]
y_reg   = np.log1p(df["actual_time_min"])   # log‑transform target

print(f"🧮  Feature matrix shape: {X.shape}")

# ── 4. Train/test splits ─────────────────────────────────────────────────
Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
    X, y_class, test_size=0.2, random_state=42, stratify=y_class
)
Xr_tr, Xr_te, yr_tr, yr_te = train_test_split(
    X, y_reg, test_size=0.2, random_state=42
)

# ── 5. Class weights & sample weights ────────────────────────────────────
classes        = np.array([0, 1, 2])
class_weights  = compute_class_weight("balanced", classes=classes, y=yc_tr)
sample_weight  = yc_tr.map(dict(zip(classes, class_weights))).values
print("⚖️  Class weights:", dict(zip(classes, class_weights)))

# ── 6. Train XGBoost classifier ───────────────────────────────────────────
print("🎯  Training XGBoost classifier …")
clf = XGBClassifier(
    objective="multi:softprob",
    num_class=3,
    n_estimators=100,
    max_depth=5,
    learning_rate=0.12,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1,
    reg_lambda=1,
    random_state=42,
    n_jobs=-1,
    tree_method="hist",
)
clf.fit(Xc_tr, yc_tr, sample_weight=sample_weight)

y_pred = clf.predict(Xc_te)
print("\n📊  Classification Report (test):")
print(classification_report(
      yc_te, y_pred, digits=3,
      target_names=["On Time", "Delayed", "Very Delayed"]))
print("Balanced Accuracy:", balanced_accuracy_score(yc_te, y_pred))

# ── 7. Train Random‑Forest regressor (log‑target) ────────────────────────
print("\n📈  Training Random‑Forest regressor (log‑target) …")
reg = RandomForestRegressor(
    n_estimators=100,
    max_depth=12,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1,
)
reg.fit(Xr_tr, yr_tr)

# Predict & invert log scale
yr_pred_log = reg.predict(Xr_te)
yr_pred     = np.expm1(yr_pred_log)
yr_true     = np.expm1(yr_te)

mae  = mean_absolute_error(yr_true, yr_pred)
rmse = sqrt(mean_squared_error(yr_true, yr_pred))
print(f"🧪  Regression MAE:  {mae:.2f} min  |  RMSE: {rmse:.2f} min")

# ── 8. Save models ───────────────────────────────────────────────────────
joblib.dump(clf, CLF_PATH)
joblib.dump(reg, REG_PATH)
print(f"💾  Saved classifier → {CLF_PATH}")
print(f"💾  Saved regressor  → {REG_PATH}")

print(f"\n✅  Training completed in {time.time()-t0:.1f}s")

# scripts/train_model.py

import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, mean_absolute_error, mean_squared_error
from math import sqrt
INPUT_PATH = "data/feature_data.csv"
CLASSIFIER_PATH = "models/classifier.pkl"
REGRESSOR_PATH = "models/regressor.pkl"

def train_models():
    df = pd.read_csv(INPUT_PATH)
    df.drop(columns=["delivery_id"], errors="ignore", inplace=True)

    feature_cols = ['from_zone', 'to_zone', 'time_slot', 'traffic', 'weather', 'weight_kg', 'distance_km']
    X = df[feature_cols]
    y_class = df["delay_label"]
    y_reg = df["actual_time_min"]

    X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_class, test_size=0.2, random_state=42)
    X_train_r, X_test_r, y_train_r, y_test_r = train_test_split(X, y_reg, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train_c, y_train_c)
    print("📊 Classification Report:")
    print(classification_report(y_test_c, clf.predict(X_test_c)))

    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_train_r, y_train_r)
    print("📈 Regression Metrics:")
    print("MAE:", round(mean_absolute_error(y_test_r, reg.predict(X_test_r)), 2))
    print("RMSE:", round(sqrt(mean_squared_error(y_test_r, reg.predict(X_test_r))), 2))

    os.makedirs("models", exist_ok=True)
    joblib.dump(clf, CLASSIFIER_PATH)
    joblib.dump(reg, REGRESSOR_PATH)
    print("✅ Models trained and saved to 'models/'")

if __name__ == "__main__":
    train_models()

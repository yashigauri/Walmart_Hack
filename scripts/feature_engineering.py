import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

ENCODER_PATH = "utils/encoders.pkl"
SCALER_PATH = "utils/scaler.pkl"

def label_delay(time):
    if time <= 40:
        return "On Time"
    elif time <= 70:
        return "Delayed"
    else:
        return "Very Delayed"

def feature_engineer(input_file="data/smart_combination_dataset.csv", output_file="data/feature_data.csv"):
    df = pd.read_csv(input_file)
    df["delay_label"] = df["actual_time_min"].apply(label_delay)

    # Encode categorical features
    cat_cols = ['from_zone', 'to_zone', 'time_slot', 'traffic', 'weather']
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    # Create feature matrix X for scaling
    X = df[["from_zone", "to_zone", "time_slot", "traffic", "weather", "weight_kg", "distance_km"]]
    
    # Scale ALL features (not just numerical ones)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Replace the original columns with scaled values
    df[["from_zone", "to_zone", "time_slot", "traffic", "weather", "weight_kg", "distance_km"]] = X_scaled

    # Save encoders and scaler
    os.makedirs("utils", exist_ok=True)
    joblib.dump(encoders, ENCODER_PATH)
    joblib.dump(scaler, SCALER_PATH)

    df.to_csv(output_file, index=False)
    print(f"✅ Feature-engineered data saved to '{output_file}'")
    print(f"✅ Encoders saved to '{ENCODER_PATH}'")
    print(f"✅ Scaler saved to '{SCALER_PATH}'")

def transform_features(df, encoders, for_training=False):
    """Transform input DataFrame using saved encoders and return only model input features."""
    df = df.copy()

    # Apply label encoding to categorical features
    for col, le in encoders.items():
        if col in df.columns:
            try:
                df[col] = le.transform(df[col])
            except ValueError as e:
                print(f"Warning: Unknown category in {col}. Using first class as default.")
                # Handle unknown categories by using the first class
                unknown_mask = ~df[col].isin(le.classes_)
                df.loc[unknown_mask, col] = le.classes_[0]
                df[col] = le.transform(df[col])

    # Select the same features that were used during training
    feature_columns = ["from_zone", "to_zone", "time_slot", "traffic", "weather", "weight_kg", "distance_km"]
    
    # Check if all required columns exist
    missing_cols = [col for col in feature_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    X = df[feature_columns]
    
    # Handle any NaN values
    X = X.fillna(0)
    
    return X

def load_encoders_and_scaler():
    """Load saved encoders and scaler."""
    try:
        encoders = joblib.load(ENCODER_PATH)
        scaler = joblib.load(SCALER_PATH)
        return encoders, scaler
    except FileNotFoundError as e:
        print(f"Error loading encoders/scaler: {e}")
        print("Make sure to run feature_engineer() first to create the encoders and scaler.")
        return None, None

if __name__ == "__main__":
    feature_engineer()
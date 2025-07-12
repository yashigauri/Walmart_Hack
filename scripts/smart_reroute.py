import pandas as pd
import numpy as np

def suggest_optimal_route(row, encoders, scaler, regressor):
    """
    Given a delivery row, simulate alternate combinations of from_zone and time_slot
    to find the combination with the minimum predicted delivery time.

    Returns:
        A dict with optimal combination details and predicted time.
    """
    original_zone = row["from_zone"]
    original_slot = row["time_slot"]
    original_prediction = row["predicted_time_min"]

    best_time = original_prediction
    best_combo = (original_zone, original_slot)

    suggestions = []

    # Try all combinations of zone [0–3] and time slot [0–3]
    for zone in range(4):
        for time_slot in range(4):
            temp_row = row.copy()
            temp_row["from_zone"] = zone
            temp_row["time_slot"] = time_slot

            # Prepare the row as DataFrame
            input_df = pd.DataFrame([temp_row])

            # Encode categorical features
            for col, le in encoders.items():
                input_df[col] = le.transform(input_df[col])

            # Select feature columns only
            features = input_df[
                ["from_zone", "to_zone", "time_slot", "traffic", "weather", "weight_kg", "distance_km"]
            ]

            # Scale
            features_cat = features[['from_zone', 'to_zone', 'time_slot', 'traffic', 'weather']]
            features_num = features[['weight_kg', 'distance_km']]
            features_scaled = scaler.transform(features_num.values)
            X_scaled = np.hstack([features_cat.values, features_scaled])


            # Predict time
            predicted_time = regressor.predict(X_scaled)[0]
            suggestions.append(((zone, time_slot), predicted_time))

            if predicted_time < best_time:
                best_time = predicted_time
                best_combo = (zone, time_slot)

    best_zone, best_slot = best_combo
    improvement = original_prediction - best_time

    return {
        "best_from_zone": best_zone,
        "best_time_slot": best_slot,
        "best_predicted_time": round(best_time, 2),
        "time_saved_min": round(improvement, 2)
    }

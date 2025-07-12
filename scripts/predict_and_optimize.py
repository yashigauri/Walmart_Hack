# scripts/predict_and_optimize.py

import pandas as pd
import joblib
import os
import sys
import numpy as np

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from scripts.feature_engineering import transform_features
from scripts.heatmap_generator import generate_heatmap
from scripts.rl_agent.agent_runner import get_rl_optimal_reroute

def main():
    # === Load models and tools ===
    print("🔧 Loading models and encoders...")
    try:
        scaler = joblib.load("utils/scaler.pkl")
        encoders = joblib.load("utils/encoders.pkl")
        classifier = joblib.load("models/classifier.pkl")
        regressor = joblib.load("models/regressor.pkl")
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        print("Make sure to run the training scripts first to create the models.")
        return

    # === Read input data ===
    print("📥 Reading test data...")
    input_file = "data/simulated_test_data.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return
    
    df = pd.read_csv(input_file)
    print(f"📊 Loaded {len(df)} test samples")
    print(f"📊 Test data columns: {df.columns.tolist()}")

    # === Feature engineering ===
    print("🧠 Transforming features...")
    try:
        X = transform_features(df.copy(), encoders, for_training=False)
        print(f"🔍 Features after transformation: {X.columns.tolist()}")
        print(f"🔍 Feature shape: {X.shape}")
        
        # Check what features the scaler expects
        if hasattr(scaler, 'feature_names_in_'):
            print(f"🔍 Scaler expects features: {scaler.feature_names_in_.tolist()}")
        else:
            print("🔍 Scaler doesn't have feature_names_in_ attribute")
            print(f"🔍 Scaler expects {scaler.n_features_in_} features")
        
        # Scale the features - keep as DataFrame to preserve feature names
        X_scaled = pd.DataFrame(
            scaler.transform(X),
            columns=X.columns,
            index=X.index
        )
        print("✅ Features scaled successfully")
        
    except Exception as e:
        print(f"❌ Error in feature transformation: {e}")
        print("Check if your test data has the same columns as training data:")
        print(f"Required columns: {list(encoders.keys()) + ['weight_kg', 'distance_km']}")
        return

    # === Predictions ===
    print("🔮 Running predictions...")
    try:
        # Use DataFrame for predictions to avoid sklearn warnings
        df['predicted_delay_label'] = classifier.predict(X_scaled)
        df['predicted_time_min'] = regressor.predict(X_scaled)
        print("✅ Predictions completed")
    except Exception as e:
        print(f"❌ Error in predictions: {e}")
        return

    # === Apply RL-based reroute suggestions ===
    print("🤖 Getting RL-based rerouting suggestions...")
    try:
        reroutes = []
        for idx, row in df.iterrows():
            # Convert row to ensure proper data types for RL agent
            row_dict = row.to_dict()
            
            # Ensure numeric fields are properly converted
            numeric_fields = ['weight_kg', 'distance_km', 'predicted_time_min']
            for field in numeric_fields:
                if field in row_dict:
                    try:
                        row_dict[field] = float(row_dict[field])
                    except (ValueError, TypeError):
                        print(f"⚠️ Warning: Could not convert {field} to float for row {idx}")
                        row_dict[field] = 0.0
            
            # Handle categorical fields properly - keep as strings or convert to encoded values
            categorical_fields = ['from_zone', 'to_zone', 'time_slot', 'traffic', 'weather']
            for field in categorical_fields:
                if field in row_dict:
                    # If the field is already encoded (numeric), keep it as float
                    if isinstance(row_dict[field], (int, float)):
                        row_dict[field] = float(row_dict[field])
                    # If it's a string, check if it's a string representation of a number
                    elif isinstance(row_dict[field], str):
                        try:
                            # Try to convert to float if it's a numeric string
                            row_dict[field] = float(row_dict[field])
                        except ValueError:
                            # If it's a categorical string, we need to encode it
                            if field in encoders:
                                encoder = encoders[field]
                                try:
                                    # Check if this category was seen during training
                                    if hasattr(encoder, 'classes_') and row_dict[field] in encoder.classes_:
                                        # Use the encoder to get the numeric value
                                        row_dict[field] = float(encoder.transform([row_dict[field]])[0])
                                    else:
                                        print(f"⚠️ Warning: Unknown category '{row_dict[field]}' for {field} in row {idx}")
                                        row_dict[field] = 0.0
                                except Exception:
                                    print(f"⚠️ Warning: Could not encode {field} for row {idx}")
                                    row_dict[field] = 0.0
                            else:
                                print(f"⚠️ Warning: No encoder found for {field} in row {idx}")
                                row_dict[field] = 0.0
                    else:
                        print(f"⚠️ Warning: Unexpected data type for {field} in row {idx}")
                        row_dict[field] = 0.0
            
            # Create a Series from the cleaned dict
            clean_row = pd.Series(row_dict)
            suggestion = get_rl_optimal_reroute(clean_row)
            reroutes.append(suggestion)

        reroute_df = pd.DataFrame(reroutes)
        final_df = pd.concat([df, reroute_df], axis=1)
        print("✅ RL rerouting suggestions completed")
    except Exception as e:
        print(f"❌ Error in RL rerouting: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        # Continue without RL suggestions
        final_df = df

    # === Save results ===
    print("💾 Saving results...")
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/predictions_full_report.csv"
    final_df.to_csv(output_path, index=False)
    print(f"✅ Predictions saved to '{output_path}'")

    # === Heatmap visualization ===
    print("🗺️ Generating zone-time heatmap...")
    try:
        generate_heatmap(final_df, output_path="outputs/zone_time_heatmap.png")
        print("✅ Heatmap generated")
    except Exception as e:
        print(f"❌ Error generating heatmap: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")

    print("✅ All done! Outputs generated in 'outputs/' folder.")
    
    # Print summary
    print("\n📊 SUMMARY:")
    print(f"   Total predictions: {len(final_df)}")
    if 'predicted_delay_label' in final_df.columns:
        delay_counts = final_df['predicted_delay_label'].value_counts()
        print(f"   Delay predictions: {delay_counts.to_dict()}")
    if 'predicted_time_min' in final_df.columns:
        avg_time = final_df['predicted_time_min'].mean()
        print(f"   Average predicted time: {avg_time:.2f} minutes")
    
    # Additional insights
    if 'actual_time_min' in final_df.columns and 'predicted_time_min' in final_df.columns:
        mae = np.mean(np.abs(final_df['actual_time_min'] - final_df['predicted_time_min']))
        print(f"   Mean Absolute Error: {mae:.2f} minutes")
        
    if 'suggested_route' in final_df.columns:
        route_suggestions = final_df['suggested_route'].value_counts()
        print(f"   Route suggestions: {route_suggestions.head().to_dict()}")

if __name__ == "__main__":
    main()
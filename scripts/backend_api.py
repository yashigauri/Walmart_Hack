from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import uvicorn
import os

from scripts.rl_agent.agent import DQNAgent
from scripts.rl_agent.agent_runner import get_rl_optimal_reroute
from scripts.feature_engineering import prepare_model_input

from scripts.heatmap_generator import generate_heatmap, generate_delay_heatmap

from fastapi.responses import FileResponse
from scripts.heatmap_generator import generate_heatmap, generate_delay_heatmap
# === Initialize FastAPI app ===
app = FastAPI(title="Walmart Delay + RL Rerouting API")

# === Allow CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load ML Models and Preprocessors ===
try:
    scaler = joblib.load("utils/scaler.pkl")
    encoders = joblib.load("utils/encoders.pkl")
    print("✅ Encoders loaded:")
    for feature, enc in encoders.items():
        if hasattr(enc, "classes_"):
            print(f"{feature} classes: {enc.classes_}")
        elif hasattr(enc, "categories_"):
            print(f"{feature} categories: {enc.categories_}")

    classifier = joblib.load("models/delay_classifier.pkl")
    regressor = joblib.load("models/duration_regressor.pkl")
    
    print("✅ ML models and tools loaded successfully.")
except Exception as e:
    print(f"❌ Error loading models: {e}")
    raise




# === Request Schema ===
class DeliveryInput(BaseModel):
    from_zone: str
    to_zone: str
    time_slot: str
    traffic: str
    weather: str
    weight: float
    distance: float



from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import numpy as np



# assuming encoders, scaler, classifier, regressor, get_rl_optimal_reroute are imported/initialized properly

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the error if needed here, e.g. print(exc)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import numpy as np
import traceback


# Assume encoders, scaler, classifier, regressor, get_rl_optimal_reroute are imported/initialized elsewhere

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full traceback for debugging
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )
model = joblib.load("models/delay_classifier.pkl")


@app.post("/predict")
async def predict_delay(input_data: DeliveryInput):
    try:
        raw_input = input_data.dict()
        print("📥 Raw input:", raw_input)

        # Use your original feature engineering function
        df_input = prepare_model_input(raw_input)  # Should return exactly the 14 features
        print("✅ Prepared input shape:", df_input.shape)

        if df_input.shape[1] != 14:
            raise ValueError(f"❌ Feature mismatch: expected 14, got {df_input.shape[1]}")

        # Transform
        X_scaled = scaler.transform(df_input)

        # Classification
        delay_prediction = int(classifier.predict(X_scaled)[0])
        delay_proba = float(classifier.predict_proba(X_scaled)[0][delay_prediction])

        # Regression
        log_duration = regressor.predict(X_scaled)[0]
        estimated_duration = round(np.expm1(log_duration), 2)

        return {
            "delay_class": delay_prediction,
            "delay_confidence": round(delay_proba * 100, 2),
            "estimated_duration_min": estimated_duration
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")
    
# === Supplier Score Endpoint ===
@app.get("/supplier-scores")
def get_supplier_scores():
    try:
        path = "outputs/supplier_scores.csv"
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="Supplier scores not found. Run the score engine first.")
        
        df = pd.read_csv(path)
        return df.to_dict(orient="records")
    except Exception as e:
        print("❌ Failed to load supplier scores:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cost-analysis")
@app.get("/cost-anomalies")
def get_cost_anomalies():
    try:
        base_path = "outputs/anomalies"
        all_data = []

        files = {
            "cost": "cost_outliers.csv",
            "duration": "duration_outliers.csv",
            "distance": "distance_outliers.csv"
        }

        for anomaly_type, filename in files.items():
            path = os.path.join(base_path, filename)
            if os.path.exists(path):
                df = pd.read_csv(path)
                df['anomaly_type'] = anomaly_type
                all_data.append(df)

        if not all_data:
            return []

        combined_df = pd.concat(all_data, ignore_index=True)
        combined_df = combined_df.where(pd.notnull(combined_df), None)
        combined_df.rename(columns={
            "delivery_duration_min": "duration",
            "delivery_distance_km": "distance",
            "delivery_cost": "cost"
        }, inplace=True)
        

       
        return combined_df.fillna(0).to_dict(orient="records")

    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-heatmaps")
def generate_heatmaps():
    try:
        df = pd.read_csv("outputs/predictions_full_report.csv")
        generate_heatmap(df, output_path="outputs/zone_time_heatmap.png")
        generate_delay_heatmap(df, output_path="outputs/delay_heatmap_by_time_slot.png")
        return {"message": "✅ Heatmaps generated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating heatmaps: {str(e)}")

@app.get("/heatmap/{name}")
def get_heatmap(name: str):
    filepath = f"outputs/{name}"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Heatmap not found")
    return FileResponse(filepath, media_type="image/png")
# === Run app manually ===
if __name__ == "__main__":
    uvicorn.run("scripts.backend_api:app", host="0.0.0.0", port=8000, reload=True)
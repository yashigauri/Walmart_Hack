from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import torch
import uvicorn
import os

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Walmart Delay + RL Rerouting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Load models and tools ===
scaler = joblib.load("utils/scaler.pkl")
encoders = joblib.load("utils/encoders.pkl")
classifier = joblib.load("models/classifier.pkl")
regressor = joblib.load("models/regressor.pkl")

# RL agent loading
def load_rl_agent():
    from scripts.rl_agent.agent import DQNAgent
    agent = DQNAgent(state_size=4, action_size=3)
    agent.load("models/rl_agent.pth")
    return agent

rl_agent = load_rl_agent()

# Import feature pipeline
from scripts.feature_engineering import transform_features

# === Request Schema ===
class DeliveryInput(BaseModel):
    from_zone: str
    to_zone: str
    time_slot: str
    traffic: str
    weather: str
    weight_kg: float
    distance_km: float

# === RL State Builder ===
def build_rl_state(row):
    from_zone_map = {"ZoneA": 0, "ZoneB": 1, "ZoneC": 2, "ZoneD": 3}
    time_slot_map = {"Morning": 0, "Afternoon": 0.3, "Evening": 0.6, "Night": 1.0}
    traffic_map = {"Low": 0.0, "Medium": 1.0, "High": 2.0}

    from_zone = from_zone_map.get(row['from_zone'], 0) / 3
    time_slot = time_slot_map.get(row['time_slot'], 0.5)
    traffic = traffic_map.get(row['traffic'], 1.0)
    distance = row['distance_km']

    # Normalize distance if needed
    distance_scaled = (distance - 0) / (100)  # assuming max 100 km

    return [from_zone, traffic / 2, distance_scaled, time_slot]

# === RL Prediction ===
def get_rl_action(state):
    state_index = rl_agent.get_state_index(state)
    q_values = rl_agent.q_table[state_index]
    action_idx = int(np.argmax(q_values))
    actions = ["Continue", "Reroute_A", "Reroute_B"]
    return actions[action_idx]


# === Predict Route ===
@app.post("/predict")
def predict(input_data: DeliveryInput):
    try:
        # Convert to DataFrame
        df = pd.DataFrame([input_data.dict()])

        # Transform
        X = transform_features(df.copy(), encoders, for_training=False)
        X_scaled = scaler.transform(X)

        # Predict
        delay_label = classifier.predict(X_scaled)[0]
        delay_time = regressor.predict(X_scaled)[0]

        # RL reroute
        state = build_rl_state(input_data.dict())
        action = get_rl_action(state)

        return {
            "predicted_delay_label": delay_label,
            "predicted_time_min": round(delay_time, 2),
            "rl_action": action,
            "rl_state": state
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === Run (only if this script is executed directly) ===
if __name__ == "__main__":
    uvicorn.run("scripts.backend_api:app", host="0.0.0.0", port=8000, reload=True)

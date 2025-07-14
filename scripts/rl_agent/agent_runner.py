"""
Utility wrapper: load the trained DQN once and expose
get_rl_optimal_reroute(delivery_row) for the rest of the code‑base.
"""
import os, numpy as np, pandas as pd
from .agent import DQNAgent
from math import log1p

MODEL_PATH = "models/rl_dqn.pth"

# ------------------------------------------------ feature engineering helpers
def _engineer(row):
    d = dict(row) if isinstance(row, (pd.Series, dict)) else {}
    dist = float(d.get("distance_km", 0))
    w    = float(d.get("weight_kg", 0))
    tmin = float(d.get("actual_time_min", d.get("predicted_time_min", 60)))
    feats = {
        "distance_km"              : dist,
        "weight_kg"                : w,
        "same_zone"                : float(d.get("same_zone", 0)),
        "efficiency_km_per_min"    : dist / (tmin + 1),
        "distance_per_kg"          : dist / (w + 1),
        "avg_speed_kmh"            : dist / ((tmin + 1) / 60),
        "log_distance"             : log1p(dist),
        "weight_to_distance_ratio" : w / (dist + 1),
        "traffic"                  : float(d.get("traffic", 0.5)),
        "weather"                  : float(d.get("weather", 0.5)),
        "time_slot_morning"        : 1.0 if d.get("time_slot") == "morning" else 0.0,
        "weight_category_heavy"    : 1.0 if d.get("weight_category") == "heavy" else 0.0,
    }
    return np.array(list(feats.values()), dtype=np.float32)


class RLAgentRunner:
    _actions = ["Continue", "Reroute_A", "Reroute_B"]

    def __init__(self, path: str = MODEL_PATH):
        self.agent = DQNAgent()
        if os.path.exists(path):
            self.agent.load(path)
            self.agent.epsilon = 0.0   # no exploration in prod
        else:
            print(f"⚠️  DQN model not found at {path}. Using un‑trained agent.")

    def predict(self, delivery_row):
        s = _engineer(delivery_row)
        a = self.agent.act(s, explore=False)
        return {
            "rl_action"      : self._actions[a],
            "rl_action_id"   : int(a),
            "rl_confidence"  : 1.0,  # placeholder (could derive from Q spread)
        }


# public helper -------------------------------------------------------------
_runner = RLAgentRunner()   # singleton

def get_rl_optimal_reroute(delivery_row):
    """Thin façade used by other modules."""
    return _runner.predict(delivery_row)


# quick manual test
if __name__ == "__main__":
    demo = {
        "distance_km": 15.5, "weight_kg": 25, "actual_time_min": 90,
        "same_zone": 0, "traffic": 0.7, "weather": 0.3,
        "time_slot": "morning", "weight_category": "heavy"
    }
    print(get_rl_optimal_reroute(demo))

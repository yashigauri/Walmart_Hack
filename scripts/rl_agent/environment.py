"""
DeliveryEnv — contextual‑bandit environment for smart rerouting
action 0 : keep current plan
action 1 : moderate reroute   (lower risk, small cost)
action 2 : aggressive reroute (highest cost, highest benefit)
Reward is + if we cut delay risk / travel time, – if we hurt it.
"""
import numpy as np, pandas as pd
from math import log1p
import gymnasium as gym
from gymnasium import spaces


_NUMERIC = [
    "distance_km", "weight_kg", "same_zone",
    "efficiency_km_per_min", "distance_per_kg", "avg_speed_kmh",
    "log_distance", "weight_to_distance_ratio",
]
_OBS_DIM = len(_NUMERIC) + 4  # + traffic + weather + two 1‑hot flags


class DeliveryEnv(gym.Env):
    metadata: dict = {"render.modes": []}

    def __init__(self, delivery_df: pd.DataFrame):
        super().__init__()
        self.df = delivery_df.copy().reset_index(drop=True)
        self._prep_features()
        # ── observation & action spaces ─────────────────────
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(_OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)  # 0/1/2

    # --------------------------------------------------------------------- utils
    def _prep_features(self):
        """feature engineering & normalisation stats (min–max)."""
        if "delay_label" not in self.df:
            self.df["delay_label"] = (self.df["actual_time_min"] > 90).astype(int)

        # replicate features from train_model.py
        self.df["efficiency_km_per_min"] = self.df["distance_km"] / (
            self.df["actual_time_min"] + 1
        )
        self.df["distance_per_kg"] = self.df["distance_km"] / (
            self.df["weight_kg"] + 1
        )
        self.df["avg_speed_kmh"] = self.df["distance_km"] / (
            (self.df["actual_time_min"] + 1) / 60
        )
        self.df["log_distance"] = self.df["distance_km"].apply(log1p)
        self.df["weight_to_distance_ratio"] = self.df["weight_kg"] / (
            self.df["distance_km"] + 1
        )
        # default columns if missing
        self.df["traffic"] = self.df.get("traffic", 0.5)
        self.df["weather"] = self.df.get("weather", 0.5)
        self.df["time_slot"] = self.df.get("time_slot", "morning")
        self.df["weight_category"] = self.df.get("weight_category", "medium")

        # stats for min‑max scaling
        self.stats = {c: (self.df[c].min(), self.df[c].max()) for c in _NUMERIC}

    def _norm(self, v, col):
        mn, mx = self.stats[col]
        return 0.0 if mx == mn else (v - mn) / (mx - mn)

    def _make_obs(self, row: pd.Series) -> np.ndarray:
        obs = [
            self._norm(row[c], c) for c in _NUMERIC
        ] + [
            float(row["traffic"]),
            float(row["weather"]),
            1.0 if row["time_slot"] == "morning" else 0.0,
            1.0 if row["weight_category"] == "heavy" else 0.0,
        ]
        return np.asarray(obs, dtype=np.float32)

    # ---------------------------------------------------------------- gym API
    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self.idx = self.np_random.integers(0, len(self.df))
        self.cur = self.df.iloc[self.idx]
        self.base_delay_flag = int(self.cur["delay_label"])
        obs = self._make_obs(self.cur)
        return obs, {}

    def step(self, action: int):
        """
        Reward structure (simple but aligns with old prototype):
            • Keeping an on‑time parcel ⇒ +10
            • Keeping a delayed parcel ⇒ –10
            • Reroute_A   (1):
                  if delayed →  +8  | else −3
            • Reroute_B   (2):
                  if delayed → +12 | else −8
        Small shaping bonuses based on efficiency / load difficulty.
        """
        delayed = self.base_delay_flag
        if action == 0:
            rew = 10 if delayed == 0 else -10
        elif action == 1:
            rew = 8 if delayed == 1 else -3
        else:
            rew = 12 if delayed == 1 else -8

        # efficiency shaping
        if self.cur["efficiency_km_per_min"] > self.df["efficiency_km_per_min"].mean():
            rew += 2
        elif self.cur["efficiency_km_per_min"] < 0.7 * self.df["efficiency_km_per_min"].mean():
            rew -= 2
        # load difficulty penalty
        if self.cur["weight_to_distance_ratio"] > 1.5 * self.df["weight_to_distance_ratio"].mean():
            rew -= 1

        info = {
            "delivery_id": self.cur.get("delivery_id", f"row_{self.idx}"),
            "delay": bool(delayed),
            "action": action,
            "reward_components": rew
        }
        obs = self._make_obs(self.cur)  # not used again (one‑step bandit)
        terminated, truncated = True, False
        return obs, float(rew), terminated, truncated, info

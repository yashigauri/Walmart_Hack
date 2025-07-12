# rl_agent/environment.py

import gym
import numpy as np
import pandas as pd
from gym import spaces

class DeliveryEnv(gym.Env):
    def __init__(self, delivery_df):
        super(DeliveryEnv, self).__init__()
        self.df = delivery_df.copy()
        self.current_index = 0

        # Create predicted_time_min if it doesn't exist
        if 'predicted_time_min' not in self.df.columns:
            # Simple prediction: base time from distance + traffic factor
            # You can replace this with your actual ML model predictions
            base_time = self.df['distance_km'] * 2  # 2 minutes per km
            traffic_factor = 1 + (self.df['traffic'] * 0.5)  # traffic adds delay
            weather_factor = 1 + (self.df['weather'] * 0.2)  # weather adds delay
            weight_factor = 1 + (self.df['weight_kg'] / 100)  # weight adds delay
            
            self.df['predicted_time_min'] = base_time * traffic_factor * weather_factor * weight_factor

        # Add zone_importance if missing
        if 'zone_importance' not in self.df.columns:
            self.df['zone_importance'] = self.df['from_zone'] * 2 + self.df['to_zone']

        # Define observation and action spaces
        self.observation_space = spaces.Box(low=0, high=1, shape=(4,), dtype=np.float32)  # [location, traffic, delay_status, zone_importance]
        self.action_space = spaces.Discrete(3)  # 0: Continue, 1: Reroute_A, 2: Reroute_B

    def reset(self):
        self.current_index = np.random.randint(0, len(self.df))
        obs = self._get_obs()
        return obs

    def _get_obs(self):
        row = self.df.iloc[self.current_index]
        return np.array([
            row['from_zone'] / 3,  # Normalize assuming max zone is 3
            row['traffic'],  # Already normalized 0-1
            row['predicted_time_min'] / 200,  # Normalize time
            row.get('zone_importance', 5) / 10  # Normalize zone importance
        ], dtype=np.float32)

    def step(self, action):
        row = self.df.iloc[self.current_index]
        predicted_delay = row["predicted_time_min"]
        actual_time = row["actual_time_min"]
        delay_label = row["delay_label"]
        
        # Calculate reward based on action and actual outcome
        if action == 0:  # Continue with original route
            if delay_label == 'On Time':
                reward = 10.0  # Good decision
            elif delay_label == 'Delayed':
                reward = -5.0  # Moderate penalty
            else:  # Very Delayed
                reward = -15.0  # High penalty
        elif action == 1:  # Reroute via A (conservative, 10% improvement)
            if delay_label == 'Very Delayed':
                reward = 8.0  # Good preventive action
            elif delay_label == 'Delayed':
                reward = 3.0  # Reasonable action
            else:  # On Time
                reward = -2.0  # Unnecessary reroute
        else:  # Reroute via B (aggressive, 15% improvement)
            if delay_label == 'Very Delayed':
                reward = 12.0  # Excellent preventive action
            elif delay_label == 'Delayed':
                reward = 1.0  # Reasonable action
            else:  # On Time
                reward = -5.0  # Unnecessary aggressive reroute

        # Add penalty for prediction error
        prediction_error = abs(actual_time - predicted_delay) / max(actual_time, 1)
        reward -= prediction_error * 2

        done = True
        info = {
            'delivery_id': row['delivery_id'],
            'actual_delay': actual_time,
            'predicted_delay': predicted_delay,
            'delay_label': delay_label
        }
        
        return self._get_obs(), reward, done, info

    def render(self, mode='human'):
        """Render environment (optional)"""
        row = self.df.iloc[self.current_index]
        print(f"Delivery {row['delivery_id']}: {row['from_zone']} -> {row['to_zone']}")
        print(f"Traffic: {row['traffic']:.2f}, Distance: {row['distance_km']:.1f}km")
        print(f"Predicted: {row['predicted_time_min']:.1f}min, Actual: {row['actual_time_min']:.1f}min")
        print(f"Status: {row['delay_label']}")

# Test the environment if run directly
if __name__ == "__main__":
    # Create some dummy data for testing
    test_data = pd.DataFrame({
        'delivery_id': ['A', 'B', 'C', 'D', 'E'],
        'from_zone': [1, 2, 3, 1, 2],
        'to_zone': [2, 3, 1, 3, 1],
        'time_slot': [0, 1, 2, 0, 1],
        'traffic': [0.5, 0.7, 0.3, 0.8, 0.4],
        'weather': [0.2, 0.5, 0.1, 0.8, 0.3],
        'weight_kg': [10, 25, 15, 30, 20],
        'distance_km': [5, 8, 3, 12, 6],
        'actual_time_min': [45, 60, 30, 75, 40],
        'delay_label': ['On Time', 'Delayed', 'On Time', 'Very Delayed', 'Delayed']
    })
    
    env = DeliveryEnv(test_data)
    obs = env.reset()
    print("Initial observation:", obs)
    
    action = env.action_space.sample()  # Random action
    obs, reward, done, info = env.step(action)
    print(f"Action: {action}, Reward: {reward}, Done: {done}")
    print("Info:", info)
    print("Environment created successfully!")
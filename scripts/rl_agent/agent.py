# scripts/rl_agent/agent.py

import numpy as np
import pandas as pd
from collections import deque
import random
import os
class DQNAgent:
    """
    Simple DQN Agent for route optimization
    """
    
    def __init__(self, state_size=10, action_size=5, learning_rate=0.001):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.learning_rate = learning_rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        
        # For simplicity, using a basic policy without neural networks
        # In production, you'd use TensorFlow/PyTorch here
        self.q_table = np.random.uniform(low=-1, high=1, size=(100, action_size))
        
    def get_state_index(self, state):
        """Convert state to index for Q-table lookup"""
        # Simple hash function for demonstration
        return hash(str(state)) % 100
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in memory"""
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        """Choose action using epsilon-greedy policy"""
        if np.random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        
        state_index = self.get_state_index(state)
        return np.argmax(self.q_table[state_index])
    
    def replay(self, batch_size=32):
        """Train the agent on a batch of experiences"""
        if len(self.memory) < batch_size:
            return
        
        batch = random.sample(self.memory, batch_size)
        
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                next_state_index = self.get_state_index(next_state)
                target = reward + 0.95 * np.amax(self.q_table[next_state_index])
            
            state_index = self.get_state_index(state)
            target_f = self.q_table[state_index].copy()
            target_f[action] = target
            self.q_table[state_index] = target_f
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load_model(self, model_path):
        import torch
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
            self.q_table = checkpoint['q_table']
            print(f"✅ Model loaded from {model_path}")
        else:
            print(f"⚠️ Model file {model_path} not found. Using random initialization.")
    

    def save_model(self, model_path):
        import torch
        torch.save({'q_table': self.q_table}, model_path)
        print(f"✅ Model saved to {model_path}")

    def get_optimal_action(self, state):
        """Get the optimal action for a given state"""
        state_index = self.get_state_index(state)
        return np.argmax(self.q_table[state_index])
    
    def get_reroute_suggestion(self, delivery_data):
        """
        Get reroute suggestion based on delivery data
        
        Args:
            delivery_data: Dictionary or Series with delivery information
            
        Returns:
            Dictionary with reroute suggestions
        """
        # Extract relevant features for state representation
        if isinstance(delivery_data, pd.Series):
            delivery_data = delivery_data.to_dict()
        
        # Create state vector from delivery data
        # Convert all values to float to avoid type errors
        state_features = [
            float(delivery_data.get('distance_km', 0)),
            float(delivery_data.get('traffic', 0)),  # Use 'traffic' instead of 'traffic_density'
            float(delivery_data.get('weather', 0)),  # Use 'weather' instead of 'weather_condition'
            float(delivery_data.get('weight_kg', 0)),
            float(delivery_data.get('predicted_delay_label', 0)) if isinstance(delivery_data.get('predicted_delay_label'), (int, float)) else 0.0,
            float(delivery_data.get('predicted_time_min', 0)),
            float(delivery_data.get('from_zone', 0)),
            float(delivery_data.get('to_zone', 0)),
            float(delivery_data.get('time_slot', 0)),
            float(delivery_data.get('delivery_id', 0))
        ]
        
        # Get optimal action
        optimal_action = self.get_optimal_action(state_features)
        
        # Map action to reroute suggestion
        action_mapping = {
            0: {"reroute_needed": False, "suggested_route": "current", "priority_change": 0},
            1: {"reroute_needed": True, "suggested_route": "highway", "priority_change": 1},
            2: {"reroute_needed": True, "suggested_route": "local_roads", "priority_change": 0},
            3: {"reroute_needed": True, "suggested_route": "express_lane", "priority_change": 2},
            4: {"reroute_needed": True, "suggested_route": "alternate_zone", "priority_change": -1}
        }
        
        suggestion = action_mapping.get(optimal_action, action_mapping[0])
        
        # Add confidence score
        state_index = self.get_state_index(state_features)
        q_values = self.q_table[state_index]
        confidence = (np.max(q_values) - np.min(q_values)) / (np.max(q_values) + 1e-8)
        suggestion["confidence"] = min(max(confidence, 0), 1)
        
        return suggestion
    
    def load(self, path):
        self.load_model(path)
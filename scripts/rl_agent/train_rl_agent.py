# rl_agent/train_rl_agent.py
import pandas as pd
import torch
import os
import sys
import numpy as np

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environment import DeliveryEnv
from agent import DQNAgent

def train():
    # Load data
    df = pd.read_csv(r'C:\Users\kksin\Documents\walmart_delay_prediction\data\feature_data.csv')
    
    print("📊 Data loaded successfully!")
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Check for required columns
    required_cols = ['from_zone', 'traffic', 'actual_time_min', 'delay_label', 'distance_km']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        print(f"❌ Missing required columns: {missing_cols}")
        return
    
    print("✅ All required columns found!")
    print(f"Unique delay labels: {df['delay_label'].unique()}")
    print(f"Traffic range: {df['traffic'].min():.2f} - {df['traffic'].max():.2f}")
    print(f"Distance range: {df['distance_km'].min():.1f} - {df['distance_km'].max():.1f} km")
    print(f"Actual time range: {df['actual_time_min'].min():.1f} - {df['actual_time_min'].max():.1f} min")
    
    # Create environment and agent
    env = DeliveryEnv(df)
    
    # Create agent with correct parameter names matching your implementation
    agent = DQNAgent(state_size=4, action_size=3, learning_rate=0.001)
    print("✅ Agent created successfully!")
    
    print("🚀 Starting RL Agent Training...")
    print(f"Training on {len(df)} delivery records")
    
    for episode in range(1000):
        state = env.reset()
        done = False
        total_reward = 0
        step_count = 0
        max_steps = 100  # Prevent infinite loops
        
        while not done and step_count < max_steps:
            # Use agent's built-in act method (includes epsilon-greedy)
            action = agent.act(state)
            
            next_state, reward, done, _ = env.step(action)
            total_reward += reward
            
            # Store experience and train
            agent.remember(state, action, reward, next_state, done)
            agent.replay()  # This handles the training
            
            state = next_state
            step_count += 1
            
        # Update target network every 100 episodes (not needed for Q-table but kept for consistency)
        if episode % 100 == 0 and episode > 0:
            # Your agent uses Q-table, so no target network update needed
            pass
            
        if episode % 50 == 0:
            avg_reward = total_reward / max(step_count, 1)
            print(f"Episode {episode}, Total Reward: {total_reward:.2f}, Avg Reward: {avg_reward:.2f}, Epsilon: {agent.epsilon:.3f}, Steps: {step_count}")
            
            # Show some action distribution
            if episode % 200 == 0 and episode > 0:
                print(f"  -> Current exploration rate: {agent.epsilon:.3f}")
                # Test a few states to see action preferences
                test_states = []
                for i in range(min(5, len(df))):
                    test_env = DeliveryEnv(df.iloc[i:i+1])
                    test_state = test_env.reset()
                    test_states.append(test_state)
                
                actions = [agent.act(state) for state in test_states]
                action_names = ["Continue", "Reroute_A", "Reroute_B"]
                print(f"  -> Sample actions: {[action_names[a] for a in actions]}")
    
    # Create models directory if it doesn't exist
    os.makedirs("../models", exist_ok=True)
    
    # Save the trained model
    model_path = "../models/rl_agent.npy"  # Use .npy extension for numpy array
    agent.save_model(model_path)
    print(f"✅ RL Agent trained and saved to {model_path}")
    
    # Test the saved model
    print("\n🧪 Testing saved model...")
    test_agent = DQNAgent(state_size=4, action_size=3, learning_rate=0.001)
    test_agent.load_model(model_path)
    test_agent.epsilon = 0.0  # No exploration for testing
    
    # Test on a few examples
    for i in range(3):
        state = env.reset()
        action = test_agent.act(state)
        action_names = ["Continue", "Reroute_A", "Reroute_B"]
        print(f"Test {i+1}: State = {state}, Action = {action_names[action]}")
    
    return agent

if __name__ == "__main__":
    train()
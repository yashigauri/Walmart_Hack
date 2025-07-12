# rl_agent/agent_runner.py

import numpy as np
import pandas as pd
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Now use absolute import
try:
    from scripts.rl_agent.agent import DQNAgent
except ImportError:
    print("⚠️ Warning: Could not import DQNAgent. Using fallback mode.")
    DQNAgent = None

class RLAgentRunner:
    def __init__(self, model_path="../models/rl_agent.npy"):
        self.model_path = model_path
        self.agent = None
        self.load_agent()
    
    def load_agent(self):
        """Load the trained RL agent"""
        if os.path.exists(self.model_path):
            try:
                if DQNAgent is not None:
                    # Use correct parameter names for your DQNAgent
                    self.agent = DQNAgent(state_size=4, action_size=3, learning_rate=0.001)
                    self.agent.load_model(self.model_path)
                    self.agent.epsilon = 0.0  # No exploration for production
                    print(f"✅ RL Agent loaded from {self.model_path}")
                else:
                    print("⚠️ DQNAgent class not available, using fallback mode")
            except Exception as e:
                print(f"❌ Error loading RL agent: {e}")
                print("Using fallback mode.")
        else:
            print(f"❌ Model not found at {self.model_path}")
            print("Please train the model first using train_rl_agent.py")
    
    def preprocess_delivery_data(self, delivery_row):
        """Preprocess delivery data to match training format"""
        # Convert to dict if it's a Series
        if isinstance(delivery_row, pd.Series):
            delivery_data = delivery_row.to_dict()
        else:
            delivery_data = delivery_row.copy()
        
        # Ensure all values are numeric and properly typed
        numeric_fields = {
            'from_zone': 1.0,
            'to_zone': 2.0,
            'time_slot': 0.0,
            'traffic': 0.5,
            'weather': 0.3,
            'weight_kg': 10.0,
            'distance_km': 10.0,
            'predicted_time_min': 60.0
        }
        
        for field, default_value in numeric_fields.items():
            if field in delivery_data:
                try:
                    # Handle string representations of numbers
                    if isinstance(delivery_data[field], str):
                        delivery_data[field] = float(delivery_data[field])
                    else:
                        delivery_data[field] = float(delivery_data[field])
                except (ValueError, TypeError):
                    print(f"⚠️ Warning: Could not convert {field}, using default {default_value}")
                    delivery_data[field] = default_value
            else:
                delivery_data[field] = default_value
        
        # Create predicted_time_min if not exists
        if 'predicted_time_min' not in delivery_data or delivery_data['predicted_time_min'] <= 0:
            base_time = delivery_data['distance_km'] * 2
            traffic_factor = 1 + (delivery_data['traffic'] * 0.5)
            weather_factor = 1 + (delivery_data['weather'] * 0.2)
            weight_factor = 1 + (delivery_data['weight_kg'] / 100)
            delivery_data['predicted_time_min'] = base_time * traffic_factor * weather_factor * weight_factor
        
        # Create zone_importance if not exists
        if 'zone_importance' not in delivery_data:
            delivery_data['zone_importance'] = delivery_data['from_zone'] * 2 + delivery_data['to_zone']
        
        return delivery_data
    
    def get_state_from_delivery(self, delivery_row):
        """Convert delivery row to state vector"""
        delivery_data = self.preprocess_delivery_data(delivery_row)
        
        # Ensure all values are numeric and within reasonable ranges
        from_zone = max(0, min(3, delivery_data['from_zone']))  # Clamp to [0, 3]
        traffic = max(0, min(1, delivery_data['traffic']))        # Clamp to [0, 1]
        predicted_time = max(0, min(200, delivery_data['predicted_time_min']))  # Clamp to [0, 200]
        zone_importance = max(0, min(10, delivery_data['zone_importance']))     # Clamp to [0, 10]
        
        state = np.array([
            from_zone / 3.0,                    # Normalize assuming max zone is 3
            traffic,                            # Already normalized 0-1
            predicted_time / 200.0,             # Normalize time
            zone_importance / 10.0              # Normalize zone importance
        ], dtype=np.float32)
        
        return state
    
    def predict_action(self, delivery_row):
        """Predict the best action for a delivery"""
        if self.agent is None:
            return self.get_fallback_action(delivery_row)
        
        try:
            state = self.get_state_from_delivery(delivery_row)
            action = self.agent.act(state)
            
            action_names = ["Continue", "Reroute_A", "Reroute_B"]
            return {
                'action': int(action),
                'action_name': action_names[action],
                'confidence': self.get_action_confidence(state),
                'state': state.tolist()
            }
        except Exception as e:
            print(f"⚠️ Error in predict_action: {e}")
            return self.get_fallback_action(delivery_row)
    
    def get_action_confidence(self, state):
        """Get confidence score for the predicted action"""
        if self.agent is None:
            return 0.5
        
        try:
            # For DQN agent, we can use the Q-values to calculate confidence
            if hasattr(self.agent, 'q_network'):
                q_values = self.agent.q_network.predict(state.reshape(1, -1), verbose=0)[0]
                q_values_sorted = np.sort(q_values)[::-1]  # Sort in descending order
                if len(q_values_sorted) >= 2:
                    confidence = (q_values_sorted[0] - q_values_sorted[1]) / (q_values_sorted[0] + 1e-8)
                else:
                    confidence = 0.5
            else:
                confidence = 0.5
                
            # Normalize to [0, 1] range
            confidence = max(0, min(1, confidence))
            return confidence
        except Exception as e:
            print(f"⚠️ Error calculating confidence: {e}")
            return 0.5
    
    def get_fallback_action(self, delivery_row):
        """Fallback action when model is not available"""
        try:
            delivery_data = self.preprocess_delivery_data(delivery_row)
            traffic = delivery_data['traffic']
            distance = delivery_data['distance_km']
            
            # Simple rule-based fallback
            if traffic > 0.8 and distance > 15:
                action = 2  # Reroute_B (aggressive)
            elif traffic > 0.6 or distance > 10:
                action = 1  # Reroute_A (conservative)
            else:
                action = 0  # Continue
            
            action_names = ["Continue", "Reroute_A", "Reroute_B"]
            return {
                'action': action,
                'action_name': action_names[action],
                'confidence': 0.5,
                'state': None,
                'note': 'Fallback rule-based prediction'
            }
        except Exception as e:
            print(f"⚠️ Error in fallback action: {e}")
            return {
                'action': 0,
                'action_name': 'Continue',
                'confidence': 0.5,
                'state': None,
                'note': 'Default fallback action'
            }

def get_rl_optimal_reroute(delivery_row):
    """
    Main function to get RL agent recommendation for a delivery
    This is the function that will be called from other modules
    """
    try:
        # Initialize runner (singleton pattern)
        if not hasattr(get_rl_optimal_reroute, 'runner'):
            get_rl_optimal_reroute.runner = RLAgentRunner()
        
        runner = get_rl_optimal_reroute.runner
        prediction = runner.predict_action(delivery_row)
        
        # Safely get values from delivery_row
        if isinstance(delivery_row, pd.Series):
            to_zone = delivery_row.get('to_zone', 1)
            time_slot = delivery_row.get('time_slot', 'Morning')
            predicted_time = delivery_row.get('predicted_time_min', 60)
        else:
            to_zone = delivery_row.get('to_zone', 1)
            time_slot = delivery_row.get('time_slot', 'Morning')
            predicted_time = delivery_row.get('predicted_time_min', 60)
        
        # Ensure numeric values
        try:
            to_zone = int(float(to_zone))
            predicted_time = float(predicted_time)
        except (ValueError, TypeError):
            to_zone = 1
            predicted_time = 60.0
        
        # Convert to the expected format
        suggested_zones = {
            0: to_zone,                # Continue to original zone
            1: min(3, to_zone + 1),    # Reroute to adjacent zone
            2: min(3, to_zone + 2),    # Reroute to further zone
        }
        
        suggested_time_slots = {
            0: time_slot,      # Keep original time
            1: 'Afternoon',    # Reroute to afternoon
            2: 'Evening',      # Reroute to evening
        }
        
        # Estimate delay improvement
        delay_improvements = {
            0: 0,    # No improvement for continue
            1: -10,  # 10 minute improvement for conservative reroute
            2: -20,  # 20 minute improvement for aggressive reroute
        }
        
        action = prediction['action']
        
        return {
            'rl_suggested_zone': suggested_zones[action],
            'rl_suggested_time_slot': suggested_time_slots[action],
            'rl_estimated_delay': predicted_time + delay_improvements[action],
            'rl_action': prediction['action_name'],
            'rl_confidence': prediction['confidence'],
            'rl_state': prediction.get('state')
        }
    except Exception as e:
        print(f"❌ Error in get_rl_optimal_reroute: {e}")
        # Return safe defaults
        return {
            'rl_suggested_zone': 1,
            'rl_suggested_time_slot': 'Morning',
            'rl_estimated_delay': 60.0,
            'rl_action': 'Continue',
            'rl_confidence': 0.5,
            'rl_state': None
        }

# Test the agent runner if run directly
if __name__ == "__main__":
    # Test data
    test_delivery = {
        'delivery_id': 'TEST001',
        'from_zone': 1,
        'to_zone': 2,
        'time_slot': 0,
        'traffic': 0.7,
        'weather': 0.3,
        'weight_kg': 25,
        'distance_km': 12,
        'actual_time_min': 45
    }
    
    # Test the function
    print("🧪 Testing RL Agent Runner...")
    result = get_rl_optimal_reroute(test_delivery)
    print("🧪 Test Result:")
    print(f"Suggested Zone: {result['rl_suggested_zone']}")
    print(f"Suggested Time: {result['rl_suggested_time_slot']}")
    print(f"Estimated Delay: {result['rl_estimated_delay']:.1f} minutes")
    print(f"Action: {result['rl_action']}")
    print(f"Confidence: {result['rl_confidence']:.3f}")
    
    # Test with multiple deliveries
    print("\n🔄 Testing with multiple deliveries:")
    test_deliveries = [
        {'from_zone': 1, 'to_zone': 2, 'traffic': 0.3, 'distance_km': 5},
        {'from_zone': 2, 'to_zone': 3, 'traffic': 0.8, 'distance_km': 15},
        {'from_zone': 3, 'to_zone': 1, 'traffic': 0.9, 'distance_km': 20},
    ]
    
    for i, delivery in enumerate(test_deliveries):
        result = get_rl_optimal_reroute(delivery)
        print(f"Delivery {i+1}: {result['rl_action']} (confidence: {result['rl_confidence']:.3f})")
    
    print("\n✅ Agent runner tested successfully!")
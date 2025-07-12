# scripts/heatmap_generator.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import os

def generate_heatmap(df, output_path="outputs/zone_time_heatmap.png"):
    """
    Generate a heatmap showing average delivery times by zone and time slot.
    Using your simplified approach.
    
    Args:
        df: DataFrame with columns 'from_zone', 'time_slot', 'predicted_time_min'
        output_path: Path to save the heatmap image
    """
    try:
        # Ensure output directory exists only if there's a directory in the path
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create directory if it's not empty
            os.makedirs(output_dir, exist_ok=True)
        
        # Use predicted_time_min if available, otherwise use actual_time_min
        time_column = 'predicted_time_min' if 'predicted_time_min' in df.columns else 'actual_time_min'
        
        if time_column not in df.columns:
            print(f"❌ Neither 'predicted_time_min' nor 'actual_time_min' found in DataFrame")
            return
            
        # Create a copy to avoid modifying the original
        df_copy = df.copy()
        
        # Create zone_time combination
        df_copy["zone_time"] = df_copy["from_zone"].astype(str) + "_" + df_copy["time_slot"].astype(str)
        
        # Calculate average delay by zone_time
        avg_delay = df_copy.groupby("zone_time")[time_column].mean().reset_index()
        
        # Split zone_time back to separate columns
        avg_delay[["zone", "time"]] = avg_delay["zone_time"].str.split("_", expand=True)
        
        # Create pivot table using modern pandas syntax
        heatmap_data = avg_delay.pivot(index="zone", columns="time", values=time_column)
        
        # Fill NaN values with 0
        heatmap_data = heatmap_data.fillna(0)
        
        # Create the heatmap
        plt.figure(figsize=(10, 6))
        sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".1f")
        plt.title("Avg Predicted Delay by Zone & Time Slot")
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✅ Heatmap saved to '{output_path}'")
        
    except Exception as e:
        print(f"❌ Error in generate_heatmap: {e}")
        print(f"Error type: {type(e).__name__}")
        print(f"Available columns: {df.columns.tolist()}")
        print(f"DataFrame shape: {df.shape}")
        raise

def generate_delay_heatmap(df, output_path="outputs/delay_heatmap.png"):
    """
    Generate a heatmap showing delay probability by zone and conditions.
    
    Args:
        df: DataFrame with delay predictions
        output_path: Path to save the heatmap image
    """
    try:
        # Ensure output directory exists only if there's a directory in the path
        output_dir = os.path.dirname(output_path)
        if output_dir:  # Only create directory if it's not empty
            os.makedirs(output_dir, exist_ok=True)
        
        if 'predicted_delay_label' not in df.columns:
            print("❌ 'predicted_delay_label' not found for delay heatmap")
            return
            
        # Create binary delay indicator (1 for any delay, 0 for on time)
        df['is_delayed'] = (df['predicted_delay_label'] != 'On Time').astype(int)
        
        # Create heatmap by zone pair and traffic conditions
        if 'traffic' in df.columns:
            delay_pivot = df.pivot_table(
                index='from_zone',
                columns='traffic',
                values='is_delayed',
                aggfunc='mean'
            ).fillna(0)
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(
                delay_pivot,
                annot=True,
                fmt='.2f',
                cmap='Reds',
                cbar_kws={'label': 'Delay Probability'},
                linewidths=0.5
            )
            
            plt.title('Delay Probability by Zone and Traffic Conditions', fontsize=14, fontweight='bold')
            plt.xlabel('Traffic Conditions', fontsize=12)
            plt.ylabel('From Zone', fontsize=12)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Delay heatmap saved to {output_path}")
        else:
            print("❌ 'traffic' column not found for delay heatmap")
            
    except Exception as e:
        print(f"❌ Error in generate_delay_heatmap: {e}")
        raise

if __name__ == "__main__":
    # Test the heatmap generator
    print("🧪 Testing heatmap generator...")
    
    # Create sample data
    np.random.seed(42)
    sample_data = pd.DataFrame({
        'from_zone': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'to_zone': np.random.choice(['A', 'B', 'C', 'D'], 100),
        'time_slot': np.random.choice(['Morning', 'Afternoon', 'Evening'], 100),
        'traffic': np.random.choice(['Low', 'Medium', 'High'], 100),
        'predicted_time_min': np.random.normal(60, 20, 100),
        'predicted_delay_label': np.random.choice(['On Time', 'Delayed', 'Very Delayed'], 100)
    })
    
    generate_heatmap(sample_data, "test_heatmap.png")
    generate_delay_heatmap(sample_data, "test_delay_heatmap.png")
    print("Test completed!")
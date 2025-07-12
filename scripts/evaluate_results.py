# scripts/evaluate_results.py

import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error
import seaborn as sns
import matplotlib.pyplot as plt

def label_delay(time):
    if time <= 40:
        return "On Time"
    elif time <= 70:
        return "Delayed"
    else:
        return "Very Delayed"

# === Load predictions
df = pd.read_csv("outputs/predictions_full_report.csv")

print("📊 Evaluating predictions...\n")

# === Recalculate true labels
df['delay_label'] = df['actual_time_min'].apply(label_delay)

# === Classification evaluation
print("🔍 Classification Report:")
print(classification_report(df['delay_label'], df['predicted_delay_label']))

# === Confusion Matrix
cm = confusion_matrix(df['delay_label'], df['predicted_delay_label'], labels=["On Time", "Delayed", "Very Delayed"])
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=["On Time", "Delayed", "Very Delayed"],
            yticklabels=["On Time", "Delayed", "Very Delayed"])
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.tight_layout()
plt.savefig("outputs/classification_confusion_matrix.png")
plt.show()

# === Regression evaluation
mae = mean_absolute_error(df['actual_time_min'], df['predicted_time_min'])
print(f"🕒 Mean Absolute Error (Delay Prediction): {mae:.2f} minutes")

# === RL Comparison (Optional)
if 'rl_estimated_delay' in df.columns:
    rl_mae = mean_absolute_error(df['actual_time_min'], df['rl_estimated_delay'])
    print(f"🚀 RL Agent MAE: {rl_mae:.2f} minutes")

    improvement = mae - rl_mae
    print(f"🎯 RL Improvement over standard regressor: {improvement:.2f} mins\n")

print("✅ Evaluation completed. Confusion matrix saved to 'outputs/classification_confusion_matrix.png'")

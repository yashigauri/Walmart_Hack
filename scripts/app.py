import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

st.set_page_config(layout="wide", page_title="Walmart Delay Predictor")

st.title("🚚 Walmart Delay Prediction Dashboard")
st.markdown("AI-powered predictions with Reinforcement Learning rerouting")

# === Load data ===
df = pd.read_csv("outputs/predictions_full_report.csv")

# === Summary ===
st.subheader("📊 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Deliveries", len(df))
col2.metric("Avg Predicted Delay", f"{df['predicted_time_min'].mean():.2f} min")
mae = (df["actual_time_min"] - df["predicted_time_min"]).abs().mean()
col3.metric("Mean Absolute Error", f"{mae:.2f} min")

# === Delay prediction distribution ===
st.subheader("🛑 Delay Category Distribution")
st.bar_chart(df['predicted_delay_label'].value_counts())

# === RL Action Breakdown ===
if 'rl_action' in df.columns:
    st.subheader("🤖 RL Agent Rerouting Actions")
    st.bar_chart(df['rl_action'].value_counts())

# === Heatmap ===
st.subheader("🗺️ Zone-Time Heatmap")
st.image("outputs/zone_time_heatmap.png", caption="Delay Heatmap by Zone & Time Slot")

# === Confusion Matrix ===
st.subheader("🧪 Classification Confusion Matrix")
st.image("outputs/classification_confusion_matrix.png", caption="Predicted vs Actual Delay Categories")

# === Data Preview ===
st.subheader("📋 Full Predictions Table")
st.dataframe(df)

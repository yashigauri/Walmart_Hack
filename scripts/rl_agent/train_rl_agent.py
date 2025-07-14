import os, time
import pandas as pd
import numpy as np
from .environment import DeliveryEnv
from .agent import DQNAgent

CSV          = "data/lade_delivery_enhanced.csv"
OUT_MODEL    = "models/rl_dqn.pth"
EPISODES     = 10_000
REPORT_EVERY = 1_000

print("📁 loading enhanced dataset …")
df = pd.read_csv(CSV)
env = DeliveryEnv(df)
agent = DQNAgent(state_size=env.observation_space.shape[0],
                 action_size=env.action_space.n)

t0 = time.time()
total_reward = 0.0

for ep in range(1, EPISODES + 1):
    # Robust reset (compatible with Gym new/old API)
    try:
        state, _ = env.reset()
    except:
        state = env.reset()

    # Convert to np.array if needed to avoid tensor warnings
    if isinstance(state, list) and isinstance(state[0], np.ndarray):
        state = np.array(state)

    action = agent.act(state)

    # Safe step unpacking (handles new/old Gym)
    try:
        next_s, reward, done, _, _ = env.step(action)  # Newer Gym
    except:
        next_s, reward, done, _ = env.step(action)     # Older Gym

    if isinstance(next_s, list) and isinstance(next_s[0], np.ndarray):
        next_s = np.array(next_s)

    agent.remember(state, action, reward, next_s, done)
    agent.train_step()
    total_reward += reward

    if ep % REPORT_EVERY == 0:
        avg_r = total_reward / REPORT_EVERY
        print(f"episode {ep:>6,d} | ε={agent.epsilon:.3f} | avg R={avg_r:6.2f}")
        total_reward = 0.0

print(f"🏁 training finished in {(time.time()-t0):.1f}s")
agent.save(OUT_MODEL)
print(f"💾 DQN model saved → {OUT_MODEL}")

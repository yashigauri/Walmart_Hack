"""
A tiny Deep‑Q‑Network (PyTorch) that matches the 12‑dim state
and 3‑actions used in DeliveryEnv.
"""
import torch, torch.nn as nn, torch.optim as optim
import random, numpy as np
from collections import deque
import os


class QNet(nn.Module):
    def __init__(self, state_sz: int, action_sz: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(state_sz, 64), nn.ReLU(),
            nn.Linear(64, 64), nn.ReLU(),
            nn.Linear(64, action_sz)
        )

    def forward(self, x):  # x: (B, state_sz)
        return self.net(x)


class DQNAgent:
    """Minimal DQN with experience replay (CPU‑only, no target‑net for brevity)."""
    def __init__(
        self,
        state_size=12,
        action_size=3,
        lr=1e-3,
        gamma=0.95,
        epsilon=1.0,
        eps_min=0.05,
        eps_decay=0.995,
        memory_cap=20_000,
        batch=128,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon, self.eps_min, self.eps_decay = epsilon, eps_min, eps_decay
        self.batch = batch

        self.mem = deque(maxlen=memory_cap)
        self.qnet = QNet(state_size, action_size)
        self.opt = optim.Adam(self.qnet.parameters(), lr=lr)
        self.loss_fn = nn.MSELoss()

    # ------------------------------------------------------------------ API
    def remember(self, s, a, r, ns, done):
        self.mem.append((s, a, r, ns, done))

    def act(self, state, explore=True) -> int:
        if explore and random.random() < self.epsilon:
            return random.randrange(self.action_size)
        # Efficient conversion of list-of-arrays to tensor
        state_arr = np.asarray(state, dtype=np.float32)
        state_t = torch.from_numpy(state_arr).unsqueeze(0)
        with torch.no_grad():
            q_vals = self.qnet(state_t)[0].cpu().numpy()
        return int(np.argmax(q_vals))

    def train_step(self):
        if len(self.mem) < self.batch:
            return
        batch = random.sample(self.mem, self.batch)
        s, a, r, ns, d = zip(*batch)

        # Efficient conversion of list-of-arrays to tensor
        s  = torch.from_numpy(np.vstack(s).astype(np.float32))
        ns = torch.from_numpy(np.vstack(ns).astype(np.float32))
        a  = torch.tensor(a, dtype=torch.int64).unsqueeze(1)
        r  = torch.tensor(r, dtype=torch.float32).unsqueeze(1)
        d  = torch.tensor(d, dtype=torch.float32).unsqueeze(1)

        q_cur = self.qnet(s).gather(1, a)
        with torch.no_grad():
            q_next = self.qnet(ns).max(1, keepdim=True)[0]
            target = r + (1 - d) * self.gamma * q_next
        loss = self.loss_fn(q_cur, target)

        self.opt.zero_grad()
        loss.backward()
        self.opt.step()

        # decay ε
        if self.epsilon > self.eps_min:
            self.epsilon *= self.eps_decay

    # ---------------------------------------------------------------- save / load
    def save(self, path: str):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(
            {
                "model": self.qnet.state_dict(),
                "epsilon": self.epsilon,
            },
            path,
        )
        print(f"💾 DQN model saved → {path}")

    def load(self, path: str):
        chk = torch.load(path, map_location="cpu")
        self.qnet.load_state_dict(chk["model"])
        self.epsilon = chk.get("epsilon", 0.0)
        print(f"✅ DQN model loaded from {path} (ε={self.epsilon:.3f})")

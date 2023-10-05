import random
import gym
import numpy as np
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
import pickle
from tqdm import trange
import os

from utils import PolynomialEpsilonDecay
from model import QNetwork


class ReplayBuffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        experience = (torch.tensor(state, dtype=torch.int64),
                      torch.tensor(action, dtype=torch.int64),
                      torch.tensor(reward, dtype=torch.float32),
                      torch.tensor(next_state, dtype=torch.int64),
                      torch.tensor(done, dtype=torch.bool))
        self.buffer[self.position] = experience
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        state, action, reward, next_state, done = zip(*random.sample(self.buffer, batch_size))
        return torch.stack(state), torch.stack(action), torch.stack(reward), torch.stack(next_state), torch.stack(done)

    def clear(self):
        self.buffer = []
        self.position = 0

    def __len__(self):
        return len(self.buffer)

def offline_train(environment, episodes, alpha, gamma, epsilon_decay_scheme, buffer_size=10000, batch_size=64):
    net = QNetwork(environment.observation_space.n, environment.action_space.n).to(device)
    optimizer = optim.Adam(net.parameters(), lr=alpha)
    criterion = nn.MSELoss()
    buffer = ReplayBuffer(buffer_size)

    outcomes = []
    epsilon = epsilon_decay_scheme.start_epsilon
    buffer_save_counter = 0

    for episode in trange(episodes, desc="Training", unit="episodes"):
        state = environment.reset()
        state = state[0]
        done = False
        outcomes.append("Failure")

        while not done:
            state_tensor = torch.eye(environment.observation_space.n)[state].unsqueeze(0).to(device)

            if np.random.random() < epsilon:
                action = environment.action_space.sample()
            else:
                with torch.no_grad():
                    action = torch.argmax(net(state_tensor)).item()

            new_state, reward, done, _, info = environment.step(action)
            buffer.push(state, action, reward, new_state, done)
            state = new_state

            if reward:
                outcomes[-1] = "Success"

        if len(buffer) == buffer_size:
            for _ in range(buffer_size // batch_size):
                states, actions, rewards, next_states, dones = buffer.sample(batch_size)

                states = torch.eye(environment.observation_space.n)[states].float().to(device)
                next_states = torch.eye(environment.observation_space.n)[next_states].float().to(device)
                target_rewards = rewards + gamma * torch.max(net(next_states), dim=1)[0] * (1 - dones.float())
                predicted_rewards = net(states).gather(1, actions.unsqueeze(-1)).squeeze(-1)

                loss = criterion(predicted_rewards, target_rewards)

                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

            # Save the buffer contents to a file
            # make dir if not exists
            if not os.path.exists("data"):
                os.makedirs("data")
            buffer_save_path = os.path.join("data", f"replay_buffer_{buffer_save_counter}.pkl")
            with open(buffer_save_path, "wb") as f:
                pickle.dump(buffer.buffer, f)

            buffer_save_counter += 1
            buffer.clear()  # Empty the buffer

            epsilon = epsilon_decay_scheme.step()

    return net, outcomes

if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    parser = argparse.ArgumentParser(
        description="Offline training with Deep Q-learning using neural network and replay buffer.")
    parser.add_argument("--model_path", type=str, default="model.pth", help="Path to save the neural network model.")
    parser.add_argument("--episodes", type=int, default=2000, help="Total number of training episodes.")
    parser.add_argument("--alpha", type=float, default=1e-4, help="Learning rate.")
    parser.add_argument("--gamma", type=float, default=0.95, help="Discount factor.")
    parser.add_argument("--start_epsilon", type=float, default=1.0, help="Starting exploration rate.")
    parser.add_argument("--end_epsilon", type=float, default=1e-5, help="Minimum exploration rate.")
    parser.add_argument("--power", type=float, default=1.5, help="Power for the polynomial decay.")
    args = parser.parse_args()

    epsilon_decay_scheme = PolynomialEpsilonDecay(args.start_epsilon, args.end_epsilon, args.episodes, args.power)

    # Load the map from the file
    with open("frozen_lake_map.pkl", "rb") as f:
        loaded_map = pickle.load(f)

    # Use the loaded map to create the environment
    env = gym.make('FrozenLake-v1', is_slippery=False, desc=loaded_map)
    model, outcomes = offline_train(env, args.episodes, args.alpha, args.gamma, epsilon_decay_scheme)

    torch.save(model.state_dict(), args.model_path)
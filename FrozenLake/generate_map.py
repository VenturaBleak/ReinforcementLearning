import gym
import numpy as np
from gym.envs.toy_text.frozen_lake import generate_random_map
import pickle

seed = 42  # Any integer seed you choose
random_map = generate_random_map(size=15)

with open("frozen_lake_map.pkl", "wb") as f:
    pickle.dump(random_map, f)
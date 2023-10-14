import torch

from game_env import GameEnv
from model import DQN
from tqdm import trange
from strategies import Strategy

##############################################################################################################
# Evaluate the model
##############################################################################################################

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
NUM_EPISODES = 2000
MAX_ROUNDS_PER_EPISODE = 5

env = GameEnv("prisoners_dilemma", render_mode=None, max_rounds=MAX_ROUNDS_PER_EPISODE)
input_dim = len(env.reset()[0][0])
output_dim = env.action_space.n

# Use the same hidden layer structure as in train.py
hidden_sizes = [64, 64, 64]

# Adjust the model instantiation
model_agent1 = DQN(input_dim, hidden_sizes, output_dim).to(device)
model_agent1.load_state_dict(torch.load(f"{env.game_modes.game_type}_agent1.pth"))
model_agent1.eval()  # Set to evaluation mode

# select opponent strategy
strategy_agent1 = Strategy(env, strategy_type="model")
strategy_agent2 = Strategy(env, strategy_type="always_defect")  # Or another strategy type

##############################################################################################################
# Evaluate the model
##############################################################################################################
for _ in trange(NUM_EPISODES):
    observations, _ = env.reset()
    observation_agent1, observation_agent2 = observations
    for _ in range(MAX_ROUNDS_PER_EPISODE):
        action_agent1 = strategy_agent1.select_action(observation_agent1, model_agent1)
        action_agent2 = strategy_agent2.select_action(observation_agent2, model_agent1)
        observations, _, terminated, _, _ = env.step(action_agent1, action_agent2)
        observation_agent1, observation_agent2 = observations

        if terminated:
            env.episode_counter += 1  # Increment episode counter after termination
            break

print(f"Agent 1 Total Cumulative Reward: {env.agent1_total_cumulative_reward}")
print(f"Agent 2 Total Cumulative Reward: {env.agent2_total_cumulative_reward}")

##############################################################################################################
# Visualize the game
##############################################################################################################

env = GameEnv("prisoners_dilemma", render_mode="human", max_rounds=MAX_ROUNDS_PER_EPISODE)


strategy_agent1 = Strategy(env, strategy_type="model")
strategy_agent2 = Strategy(env, strategy_type="always_defect")  # Or another strategy type

NUM_EPISODES = 100

for _ in range(NUM_EPISODES):
    observations, _ = env.reset()
    observation_agent1, observation_agent2 = observations
    for _ in range(MAX_ROUNDS_PER_EPISODE):
        action_agent1 = strategy_agent1.select_action(observation_agent1, model_agent1)
        action_agent2 = strategy_agent2.select_action(observation_agent2, None)
        observations, _, terminated, _, _ = env.step(action_agent1, action_agent2)
        observation_agent1, observation_agent2 = observations

        env.render()
        if terminated:
            env.episode_counter += 1  # Increment episode counter after termination
            break
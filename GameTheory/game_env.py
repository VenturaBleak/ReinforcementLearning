import gymnasium as gym
from gymnasium import spaces
import numpy as np

from game_modes import GameModes
from game_renderer import GameRenderer

class GameEnv(gym.Env):
    def __init__(self, game_type, render_mode, max_rounds=10):
        super(GameEnv, self).__init__()

        self.game_modes = GameModes(game_type)
        num_actions = len(self.game_modes.get_action_names())
        min_payoff, max_payoff = self.game_modes.get_payoff_bounds()

        self.terminated = False
        self.truncated = False

        self.action_space = spaces.Discrete(num_actions)
        self.render_mode = render_mode
        self.max_rounds = max_rounds
        self.current_round = 0
        self.total_rounds = 0
        self.episode_counter = 1  # Initialize episode counter

        # Initialize static structures with NaNs for data
        self.actions_history = np.full((self.max_rounds, 2), -1)
        self.rewards_history = np.full((self.max_rounds, 2), 0)

        # Masks initialized with zeros
        self.actions_mask = np.zeros((self.max_rounds, 2), dtype=int)
        self.payoffs_mask = np.zeros((self.max_rounds, 2), dtype=int)

        # Calculate the total dimensions for the observation space
        total_dims = len(self.reset()[0][0])  # Get the observation space for agent 1
        print("Total dimensions: ", total_dims)

        # observation space
        self.observation_space = spaces.Tuple([
            spaces.MultiDiscrete([num_actions, num_actions] * max_rounds),  # Actions history
            # spaces.Box(low=min_payoff, high=max_payoff, shape=(2 * max_rounds,), dtype=np.float32),  # Rewards history
            spaces.MultiBinary(2 * max_rounds),  # Actions mask
            # spaces.MultiBinary(2 * max_rounds),  # Rewards mask

            # Only useful, if variable game params are used, including the following:
            # payoffs
            # actions
            # number of total_players
            spaces.Discrete(max_rounds),  # Current round
            spaces.Discrete(max_rounds),  # Total rounds
            spaces.Box(low=min_payoff, high=max_payoff, shape=(num_actions ** 2,), dtype=np.float32),  # Game params
            spaces.Discrete(2),  # Player number (since we have 2 players for now)
            #spaces.Discrete(2)  # Total number of players
        ])

        # Define observation space as a Discrete space with the total dimensions
        self.observation_space = spaces.Discrete(total_dims)
#
        self.renderer = GameRenderer(self.game_modes)  # Pass instantiated GameModes object to GameRenderer

        # reset after each step
        self.agent1_action = None
        self.agent2_action = None
        self.agent1_reward = 0
        self.agent2_reward = 0

        # reset after each episode
        self.agent1_cumulative_reward = 0
        self.agent2_cumulative_reward = 0
        self.agent1_avg_reward = 0
        self.agent2_avg_reward = 0

        # never reset
        self.agent1_total_cumulative_reward = 0
        self.agent2_total_cumulative_reward = 0
        self.agent1_total_avg_reward = 0
        self.agent2_total_avg_reward = 0

    def reset(self):
        self.current_round = 0

        # Fill history with placeholders
        self.actions_history.fill(-1)
        self.rewards_history.fill(0)

        return (self._get_observation(1), self._get_observation(2)), {}

    def step(self, action_agent1, action_agent2):
        self.current_round += 1

        # get actions from both agents
        self.agent1_action = action_agent1
        self.agent2_action = action_agent2  # This is our opponent for agent1

        # get payoffs from game
        payoff = self.game_modes.get_payoff(self.agent1_action, self.agent2_action)
        self.agent1_reward = payoff[0]
        self.agent2_reward = payoff[1]

        # Store actions and payoffs in history
        self.actions_history[self.current_round - 1] = [action_agent1, action_agent2]
        self.rewards_history[self.current_round - 1] = [self.agent1_reward, self.agent2_reward]

        self.terminated = self.current_round >= self.max_rounds

        obs_agent1 = self._get_observation(1)
        obs_agent2 = self._get_observation(2)

        # episode reward
        valid_actions = ~np.isnan(self.actions_history[:self.current_round])
        valid_actions_count = valid_actions.sum()
        valid_payoffs = ~np.isnan(self.rewards_history[:self.current_round])
        valid_payoffs_count = valid_payoffs.sum()

        self.agent1_cumulative_reward += self.agent1_reward
        self.agent2_cumulative_reward += self.agent2_reward
        self.agent1_avg_reward = self.agent1_cumulative_reward / valid_actions_count
        self.agent2_avg_reward = self.agent2_cumulative_reward / valid_payoffs_count

        # total reward
        self.agent1_total_cumulative_reward += self.agent1_reward
        self.agent2_total_cumulative_reward += self.agent2_reward
        self.agent1_total_avg_reward = self.agent1_total_cumulative_reward / self.current_round
        self.agent2_total_avg_reward = self.agent2_total_cumulative_reward / self.current_round

        return (obs_agent1, obs_agent2), (payoff[0], payoff[1]), self.terminated, self.truncated, {}

    def _get_observation(self, agent_number):
        # Create masks based on the presence of -1 in actions_history
        actions_mask = np.where(self.actions_history == -1, 0, 1)
        rewards_mask = np.where(np.isnan(self.rewards_history), 0, 1)

        payoff_matrix_list = list(self.game_modes.get_payoff_matrix().reshape(-1))

        # Create a flat list for all the values in the observation
        observation = list(self.actions_history.flatten()) + \
                      list(actions_mask.flatten()) + \
                      [self.current_round, self.max_rounds] + \
                      payoff_matrix_list + \
                      [agent_number]

        return observation

    def render(self):
        if self.render_mode == 'human':
            self.renderer.render(self.agent1_action, self.agent2_action, self.agent1_reward, self.agent2_reward,
                                 self.agent1_cumulative_reward, self.agent2_cumulative_reward,
                                 self.agent1_avg_reward, self.agent2_avg_reward,
                                 self.agent1_total_cumulative_reward, self.agent2_total_cumulative_reward,
                                 self.agent1_total_avg_reward, self.agent2_total_avg_reward,
                                 self.episode_counter,
                                 self.current_round)

    def close(self):
        self.renderer.close()
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from game_modes import GameModes
from game_renderer import GameRenderer

class GameEnv(gym.Env):
    def __init__(self, game_type):
        super(GameEnv, self).__init__()

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(3)

        self.game = GameModes().get_game(game_type)
        self.renderer = GameRenderer(self.game)

        self.agent_action = None
        self.opponent_action = None
        self.reward = None

        self.agent_cumulative_reward = 0
        self.agent_avg_reward = 0
        self.opponent_cumulative_reward = 0
        self.opponent_avg_reward = 0

        self.agent_step = 0

    def reset(self):
        return 0

    def step(self, action):
        self.agent_action = action
        self.opponent_action = np.random.randint(0, self.action_space.n)
        payoff = self.game.get_payoff(self.agent_action, self.opponent_action)

        self.reward = payoff[0]
        terminated = True
        truncated = False

        self.agent_cumulative_reward += self.reward
        self.opponent_cumulative_reward += payoff[1]

        self.agent_step += 1

        self.agent_avg_reward = self.agent_cumulative_reward / self.agent_step
        self.opponent_avg_reward = self.opponent_cumulative_reward / self.agent_step

        return self.opponent_action, self.reward, terminated, truncated, {}

    def render(self, mode='human'):
        if mode == 'human':
            self.renderer.render(self.agent_action, self.opponent_action, self.reward, self.agent_cumulative_reward,
                                 self.opponent_cumulative_reward, self.agent_avg_reward, self.opponent_avg_reward)

    def close(self):
        self.renderer.close()
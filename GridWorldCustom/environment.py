import gym
from gym import spaces
import numpy as np
import pygame


class MazeGameEnv(gym.Env):
    def __init__(self, maze):
        super(MazeGameEnv, self).__init__()
        self.maze = np.array(maze)
        self.start_pos = tuple(np.array(np.where(self.maze == 'S')).reshape(-1, ))
        self.goal_pos = tuple(np.array(np.where(self.maze == 'G')).reshape(-1, ))
        self.current_pos = self.start_pos
        self.num_rows, self.num_cols = self.maze.shape
        self.action_space = spaces.Discrete(4)

        # Define observation space as Box that can hold the row and column indices
        self.observation_space = spaces.Box(low=0, high=max(self.num_rows, self.num_cols) - 1, shape=(2,),
                                            dtype=np.int32)

        pygame.init()
        self.cell_size = 40
        self.screen = pygame.display.set_mode((self.num_cols * self.cell_size, self.num_rows * self.cell_size))

    def reset(self):
        self.current_pos = self.start_pos
        return np.array(self.current_pos, dtype=np.int32)  # Convert this to a numpy array

    def step(self, action):
        new_pos = list(self.current_pos)
        if action == 0:  # Up
            new_pos[0] -= 1
        elif action == 1:  # Down
            new_pos[0] += 1
        elif action == 2:  # Left
            new_pos[1] -= 1
        elif action == 3:  # Right
            new_pos[1] += 1

        if self._is_valid_position(tuple(new_pos)):
            self.current_pos = tuple(new_pos)

        if self.current_pos == self.goal_pos:
            reward = 1.0
            done = True
        else:
            reward = 0.0
            done = False

        return np.array(self.current_pos, dtype=np.int32), reward, done, {}

    def _is_valid_position(self, pos):
        row, col = pos
        if row < 0 or col < 0 or row >= self.num_rows or col >= self.num_cols:
            return False
        if self.maze[row, col] == '#':
            return False
        return True

    def render(self):
        self.screen.fill((255, 255, 255))
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                cell_left = col * self.cell_size
                cell_top = row * self.cell_size
                if self.maze[row, col] == '#':
                    pygame.draw.rect(self.screen, (0, 0, 0), (cell_left, cell_top, self.cell_size, self.cell_size))
                elif self.maze[row, col] == 'S':
                    pygame.draw.rect(self.screen, (0, 255, 0), (cell_left, cell_top, self.cell_size, self.cell_size))
                elif self.maze[row, col] == 'G':
                    pygame.draw.rect(self.screen, (255, 0, 0), (cell_left, cell_top, self.cell_size, self.cell_size))
                if self.current_pos == (row, col):
                    pygame.draw.rect(self.screen, (0, 0, 255), (cell_left, cell_top, self.cell_size, self.cell_size))
        pygame.display.update()
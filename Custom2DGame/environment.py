"""
adapted from: https://medium.com/data-science-in-your-pocket/how-to-create-a-custom-openai-gym-environment-with-codes-fb5de015de3c
"""
import gymnasium
from gymnasium import spaces
import numpy as np
import pygame
import time

class PlainFieldEnv(gymnasium.Env):
    def __init__(self, field_size=8, vision_size=5):
        super(PlainFieldEnv, self).__init__()

        # Field dimensions
        self.num_rows = field_size
        self.num_cols = field_size

        self.vision_size = vision_size

        # Randomize start and goal positions
        self.start_pos = self._random_position()
        self.goal_pos = self._random_position()

        # Ensure start and goal positions are not the same
        while self.start_pos == self.goal_pos:
            self.goal_pos = self._random_position()

        self.current_pos = self.start_pos

        # Set facing directions
        self.facing_directions = ['N', 'S', 'W', 'E']
        self.facing_direction = np.random.choice(self.facing_directions)

        # Define action and observation space
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Box(low=0, high=1, shape=(3, 3), dtype=np.int8)

        self.steps_since_reset = 0

        # intially, the display is not initialized
        self.display_initialized = False

        # Reward dictionary
        self.rewards = {
            'move': -1.0 / field_size,
            'invalid_move': -2.0 / field_size,
            'goal_reached': 1.0,
            'truncated': -1.0
        }

        # Introducing new cell states
        self.cell_states = {
            'object_layer': {
                'empty': 0,
                'agent': 1,
                'obstacle': 2
            },
            'blocked_layer': {
                'not_blocked': 0,
                'blocked': 1
            },
            'objective_layer': {
                'none': 0,
                'start': 1,
                'goal': 2
            }
        }

        # Initialize the 3D map
        self.map = np.zeros((3, self.num_rows, self.num_cols), dtype=np.int8)

        # Populate the map for start and goal positions
        self.map[0][self.start_pos[0] - 1][self.start_pos[1] - 1] = self.cell_states['object_layer']['agent']
        self.map[1][self.start_pos[0] - 1][self.start_pos[1] - 1] = self.cell_states['blocked_layer']['blocked']
        self.map[2][self.start_pos[0] - 1][self.start_pos[1] - 1] = self.cell_states['objective_layer']['start']
        self.map[2][self.goal_pos[0] - 1][self.goal_pos[1] - 1] = self.cell_states['objective_layer']['goal']

    def reset(self, seed=None, options=None):
        if seed is not None:
            np.random.seed(seed)

        # Clear the old agent position
        self.map[0][self.current_pos[0] - 1][self.current_pos[1] - 1] = self.cell_states['object_layer']['empty']
        self.map[1][self.current_pos[0] - 1][self.current_pos[1] - 1] = self.cell_states['blocked_layer']['not_blocked']

        # Update the agent's new position
        self.current_pos = self.start_pos
        self.facing_direction = np.random.choice(self.facing_directions)

        # Set agent's position in the map
        self.map[0][self.current_pos[0] - 1][self.current_pos[1] - 1] = self.cell_states['object_layer']['agent']
        self.map[1][self.current_pos[0] - 1][self.current_pos[1] - 1] = self.cell_states['blocked_layer']['blocked']

        self.steps_since_reset = 0
        return self._get_vision(), {}

    def _random_position(self):
        x = np.random.randint(1, self.num_rows + 1)
        y = np.random.randint(1, self.num_cols + 1)
        return (x, y)

    def step(self, action):
        original_pos = self.current_pos
        new_pos = list(self.current_pos)
        if action == 0:  # Up
            new_pos[0] -= 1
        elif action == 1:  # Down
            new_pos[0] += 1
        elif action == 2:  # Left
            new_pos[1] -= 1
        elif action == 3:  # Right
            new_pos[1] += 1

        # Update facing direction based on the action
        self.facing_direction = self.facing_directions[action]

        # cost of moving
        reward = self.rewards['move']

        # Check boundaries
        if not self._is_valid_position(tuple(new_pos)):
            reward += self.rewards['invalid_move']  # Note: we're adding because the reward is negative
            self.current_pos = original_pos  # Reset to original position
        else:
            # Clear old agent position
            self.map[0][original_pos[0] - 1][original_pos[1] - 1] = self.cell_states['object_layer']['empty']
            self.map[1][original_pos[0] - 1][original_pos[1] - 1] = self.cell_states['blocked_layer']['not_blocked']

            # Update the agent's current position
            self.current_pos = tuple(new_pos)

            # Set new agent position on the map
            self.map[0][new_pos[0] - 1][new_pos[1] - 1] = self.cell_states['object_layer']['agent']
            self.map[1][new_pos[0] - 1][new_pos[1] - 1] = self.cell_states['blocked_layer']['blocked']

        # Goal check
        if self.current_pos == self.goal_pos:
            reward += self.rewards['goal_reached']
            terminated = True
        else:
            terminated = False

        # Check for truncation
        self.steps_since_reset += 1  # Increment the step counter
        truncated = self.steps_since_reset > (self.num_rows ** 2)

        if truncated:
            reward += self.rewards['truncated']

        return self._get_vision(), reward, terminated, truncated, {}

    def _is_valid_position(self, pos):
        # Check if within bounds
        if not (1 <= pos[0] <= self.num_rows and 1 <= pos[1] <= self.num_cols):
            return False

        # Check if the cell is not blocked
        if self.map[1][pos[0] - 1][pos[1] - 1] == self.cell_states['blocked_layer']['blocked']:
            return False

        return True

    def _get_vision(self):
        half_vision = self.vision_size // 2
        vision = np.zeros((self.vision_size, self.vision_size), dtype=np.int8)
        vision_coordinates = []  # To store coordinates of cells in the agent's vision

        for dx in range(-half_vision, half_vision + 1):
            for dy in range(-half_vision, half_vision + 1):
                x, y = self.current_pos[0] + dx, self.current_pos[1] + dy
                vision_coordinates.append((x, y))
                if 0 <= x <= self.num_rows and 0 <= y <= self.num_cols:  # Check if it's within the grid
                    if (x, y) == self.goal_pos:
                        vision[dx + half_vision, dy + half_vision] = 1  # 1 denotes the goal

        return vision, vision_coordinates

    def _setup_display(self):
        pygame.init()
        self.cell_size = 40
        self.screen = pygame.display.set_mode((self.num_cols * self.cell_size, self.num_rows * self.cell_size))
        self.display_initialized = True

    def render(self):
        # Initialize the pygame window if it's not set up yet
        if not self.display_initialized:
            self._setup_display()

        self.screen.fill((200, 200, 200))  # Change to light grey
        line_width = 2  # Setting a width for the boundary

        # Draw field boundary
        pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, self.num_cols * self.cell_size, self.num_rows * self.cell_size),
                         line_width)

        cell_margin = 3
        # Use the map to decide how to draw each cell
        for row in range(1, self.num_rows + 1):
            for col in range(1, self.num_cols + 1):
                cell_left = (col - 1) * self.cell_size
                cell_top = (row - 1) * self.cell_size

                # Get states from map layers
                object_state = self.map[0][row - 1][col - 1]
                blocked_state = self.map[1][row - 1][col - 1]
                objective_state = self.map[2][row - 1][col - 1]

                # Render based on object layer
                if object_state == self.cell_states['object_layer']['agent']:
                    # Get center of cell
                    center_x = int(cell_left + self.cell_size / 2)
                    center_y = int(cell_top + self.cell_size / 2)
                    half_size = int(self.cell_size / 4)

                    # Depending on the facing direction, adjust the agent's rectangle vertices
                    if self.facing_direction == 'N':
                        triangle_vertices = [(center_x, center_y - half_size),
                                             (center_x - half_size, center_y + half_size),
                                             (center_x + half_size, center_y + half_size)]
                    elif self.facing_direction == 'E':
                        triangle_vertices = [(center_x + half_size, center_y),
                                             (center_x - half_size, center_y - half_size),
                                             (center_x - half_size, center_y + half_size)]
                    elif self.facing_direction == 'S':
                        triangle_vertices = [(center_x, center_y + half_size),
                                             (center_x - half_size, center_y - half_size),
                                             (center_x + half_size, center_y - half_size)]
                    else:  # 'W'
                        triangle_vertices = [(center_x - half_size, center_y),
                                             (center_x + half_size, center_y - half_size),
                                             (center_x + half_size, center_y + half_size)]

                    pygame.draw.polygon(self.screen, (0, 0, 255),triangle_vertices)

                elif object_state == self.cell_states['object_layer']['obstacle']:
                    pygame.draw.rect(self.screen, (0, 0, 0), (cell_left, cell_top, self.cell_size, self.cell_size))

                # Render based on objective layer
                if objective_state == self.cell_states['objective_layer']['start']:
                    pygame.draw.rect(self.screen, (0, 255, 0), (
                    cell_left + cell_margin, cell_top + cell_margin, self.cell_size - 2 * cell_margin,
                    self.cell_size - 2 * cell_margin), 3)
                elif objective_state == self.cell_states['objective_layer']['goal']:
                    pygame.draw.rect(self.screen, (255, 0, 0), (
                    cell_left + cell_margin, cell_top + cell_margin, self.cell_size - 2 * cell_margin,
                    self.cell_size - 2 * cell_margin), 3)

        # Draw agent's vision using the stored vision matrix
        vision_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        vision_color = (255, 165, 0, 90)  # 30% transparent orange
        vision_surface.fill(vision_color)

        _, vision_coordinates = self._get_vision()  # We only need the coordinates here

        for x, y in vision_coordinates:
            if 1 <= x <= self.num_rows and 1 <= y <= self.num_cols:  # Ensure we are in the boundary
                cell_left = (y - 1) * self.cell_size
                cell_top = (x - 1) * self.cell_size
                self.screen.blit(vision_surface, (cell_left, cell_top))

        pygame.display.update()
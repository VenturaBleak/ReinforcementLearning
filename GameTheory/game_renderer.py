import pygame

class Styling:
    # Basic Colors
    BACKGROUND_COLOR = (255, 255, 255)  # White
    FONT_COLOR = (0, 0, 0)  # Black
    MATRIX_BORDER_COLOR = (0, 0, 0)  # Black

    AGENT1_COLOR = (173, 216, 230)  # Light blue
    AGENT2_COLOR = (255, 192, 203)  # Light red

    # Fonts
    FONT_NAME = "Arial"
    TITLE_FONT_SIZE = 40  # Larger font for the title
    DEFAULT_FONT_SIZE = 30  # Standard font size for other texts
    MATRIX_FONT_SIZE = 25  # Smaller font size for the matrix values

    # Matrix Styling
    MATRIX_CELL_BORDER_WIDTH = 1  # Border width for cells in the matrix
    MATRIX_HIGHLIGHT_RADIUS = 8  # Radius for the highlight circles in the matrix
    MATRIX_HIGHLIGHT_PADDING = 10  # Distance from the text to the highlight circle

    # Scoreboard Styling
    SCOREBOARD_HEADER_COLOR = (150, 150, 150)  # Greyish color for header
    SCOREBOARD_ROW_COLOR = (245, 245, 245)  # Very light grey for row background
    SCOREBOARD_BORDER_WIDTH = 1
    SCOREBOARD_BORDER_COLOR = (200, 200, 200)  # Light grey for borders

    # Headers & Titles
    HEADER_PADDING = 10  # Padding for headers from the top edge of their section

    # Paddings & Margins
    TITLE_PADDING_TOP = 30  # Padding from the top of the screen to the title
    SECTION_VERTICAL_MARGIN = 20  # Vertical space between different sections (like matrix and scoreboard)

class GameRenderer:
    def __init__(self, game_modes_instance):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(Styling.GAME_TITLE if hasattr(Styling, 'GAME_TITLE') else "Game Theory")

        self.game_modes = game_modes_instance
        self.game = self.game_modes.get_game()
        self.game_type = self.game_modes.game_type  # Storing the game type
        self.action_names = self.game["action_names"]

        num_actions = len(self.action_names)
        self.cell_width = 800 // (num_actions + 2)
        self.cell_height = 40

        # Initialize fonts
        self.font = pygame.font.SysFont(Styling.FONT_NAME, Styling.DEFAULT_FONT_SIZE)
        self.title_font = pygame.font.SysFont(Styling.FONT_NAME, Styling.TITLE_FONT_SIZE)
        self.matrix_font = pygame.font.SysFont(Styling.FONT_NAME, Styling.MATRIX_FONT_SIZE)

    def render(self, agent1_action, agent2_action, reward_agent1, reward_agent2,
               agent1_cumulative_reward, agent2_cumulative_reward, avg_reward_agent1, avg_reward_agent2):
        self.screen.fill(Styling.BACKGROUND_COLOR)

        # Title
        title = self.title_font.render(self.game_type, True, Styling.FONT_COLOR)  # Using self.game_type here
        title_pos = title.get_rect(center=(400, Styling.TITLE_PADDING_TOP))
        self.screen.blit(title, title_pos.topleft)

        # Displaying Payoff Matrix
        matrix_start_y = title_pos.bottom + Styling.HEADER_PADDING
        self.display_payoff_matrix(agent1_action, agent2_action, matrix_start_y)

        # Displaying Scoreboard
        scoreboard_start_y = matrix_start_y + len(self.game["action_names"]) * self.cell_height + Styling.SECTION_VERTICAL_MARGIN
        self.display_scoreboard(agent1_action, agent2_action, reward_agent1, reward_agent2,
                                agent1_cumulative_reward, agent2_cumulative_reward,
                                avg_reward_agent1, avg_reward_agent2, scoreboard_start_y)

        pygame.display.flip()
        pygame.time.wait(1000)

    def display_payoff_matrix(self, agent1_action, agent2_action, start_y):
        matrix_width = (len(self.game["action_names"]) + 1) * self.cell_width  # Fixed here
        matrix_start_x = (self.screen.get_width() - matrix_width) // 2  # Central alignment

        # Displaying the column headers
        for j, action_name in enumerate(self.game["action_names"]):
            text = self.font.render(action_name, True, Styling.FONT_COLOR)
            self.screen.blit(text, (matrix_start_x + (j + 1) * self.cell_width, start_y))

        # Draw matrix
        for i, action_name_1 in enumerate(self.game["action_names"]):  # Fixed here
            for j, action_name_2 in enumerate(self.game["action_names"]):  # Fixed here
                rect = pygame.Rect(matrix_start_x + (j + 1) * self.cell_width,
                                   start_y + (i + 1) * self.cell_height,
                                   self.cell_width, self.cell_height)
                pygame.draw.rect(self.screen, Styling.MATRIX_BORDER_COLOR, rect, Styling.MATRIX_CELL_BORDER_WIDTH)

                # Displaying the payoff values
                payoff = self.game_modes.get_payoff(i, j)
                payoff_text = f"{payoff[0]}/{payoff[1]}"
                text = self.matrix_font.render(payoff_text, True, Styling.FONT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)

                # Highlighting the agent's choices
                if i == agent1_action:
                    pygame.draw.circle(self.screen, Styling.AGENT1_COLOR, (text_rect.left - Styling.MATRIX_HIGHLIGHT_PADDING, text_rect.centery), Styling.MATRIX_HIGHLIGHT_RADIUS)
                if j == agent2_action:
                    pygame.draw.circle(self.screen, Styling.AGENT2_COLOR, (text_rect.right + Styling.MATRIX_HIGHLIGHT_PADDING, text_rect.centery), Styling.MATRIX_HIGHLIGHT_RADIUS)

            # Displaying the row headers
            text = self.font.render(action_name_1, True, Styling.FONT_COLOR)
            self.screen.blit(text, (matrix_start_x, start_y + (i + 1) * self.cell_height))

    def display_scoreboard(self, agent1_action, agent2_action, reward_agent1, reward_agent2,
                           agent1_cumulative_reward, agent2_cumulative_reward, avg_reward_agent1, avg_reward_agent2,
                           start_y):
        scoreboard_width = 3 * self.cell_width
        start_x = (self.screen.get_width() - scoreboard_width) // 2

        # Headers
        headers = ["", "Agent 1", "Agent 2"]
        for i, header in enumerate(headers):
            text = self.font.render(header, True, Styling.FONT_COLOR)
            self.screen.blit(text, (start_x + i * self.cell_width, start_y))

        rows = [
            ("Chosen Move", self.game["action_names"][agent1_action], self.game["action_names"][agent2_action]),
            ("Reward", reward_agent1, reward_agent2),
            ("", "", ""),
            ("Cum. Reward", agent1_cumulative_reward, agent2_cumulative_reward),
            ("Avg Reward", round(avg_reward_agent1, 1), round(avg_reward_agent2, 1))
        ]

        for i, (label, value_agent1, value_agent2) in enumerate(rows):
            text = self.font.render(label, True, Styling.FONT_COLOR)
            self.screen.blit(text, (start_x, start_y + (i + 1) * self.cell_height))

            text_agent1 = self.font.render(str(value_agent1), True, Styling.AGENT1_COLOR)
            self.screen.blit(text_agent1, (start_x + self.cell_width, start_y + (i + 1) * self.cell_height))

            text_agent2 = self.font.render(str(value_agent2), True, Styling.AGENT2_COLOR)
            self.screen.blit(text_agent2, (start_x + 2 * self.cell_width, start_y + (i + 1) * self.cell_height))

    def close(self):
        pygame.quit()
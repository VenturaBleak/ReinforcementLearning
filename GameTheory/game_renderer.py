import pygame


class GameRenderer:
    def __init__(self, game):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Game Theory Environment")
        self.font = pygame.font.SysFont(None, 55)
        self.game = game
        self.cell_width = 100
        self.cell_height = 30

    def render(self, agent_action, opponent_action, reward, agent_cumulative_reward, opponent_cumulative_reward,
               avg_reward_A, avg_reward_B, status="playing"):
        self.screen.fill((255, 255, 255))

        title = self.font.render("Game Theory Environment", True, (0, 0, 0))
        self.screen.blit(title, (50, 30))

        pygame.draw.rect(self.screen, (173, 216, 230), (50, 150, 250, 40))  # Light blue background for agent
        pygame.draw.rect(self.screen, (255, 192, 203), (350, 150, 250, 40))  # Light red background for opponent

        agent_text = self.font.render(f"Agent A Move: {agent_action}", True, (0, 0, 255))
        self.screen.blit(agent_text, (50, 150))

        opponent_text = self.font.render(f"Agent B Move: {opponent_action}", True, (255, 0, 0))
        self.screen.blit(opponent_text, (350, 150))

        if status == "playing":
            status_text = self.font.render("Playing move...", True, (0, 128, 0))
            self.screen.blit(status_text, (250, 100))
        else:
            decision_text_A = self.font.render(f"Agent A Decision: {agent_action}", True, (0, 0, 255))
            self.screen.blit(decision_text_A, (50, 200))

            decision_text_B = self.font.render(f"Agent B Decision: {opponent_action}", True, (255, 0, 0))
            self.screen.blit(decision_text_B, (350, 200))

        avg_reward_text_A = self.font.render(f"Avg Reward A: {avg_reward_A}", True, (0, 0, 255))
        self.screen.blit(avg_reward_text_A, (50, 250))

        avg_reward_text_B = self.font.render(f"Avg Reward B: {avg_reward_B}", True, (255, 0, 0))
        self.screen.blit(avg_reward_text_B, (350, 250))

        self.display_payoff_matrix(self.game, agent_action, opponent_action)

        pygame.display.flip()
        pygame.time.wait(1000)

    def display_payoff_matrix(self, game, agent_action, opponent_action):
        matrix = game.payoffs
        matrix_width = matrix.shape[1] * self.cell_width
        matrix_start_x = (self.screen.get_width() - matrix_width) // 2
        matrix_start_y = 300  # Some arbitrary vertical starting point

        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                if i == agent_action:
                    pygame.draw.rect(self.screen, (173, 216, 230), (
                    matrix_start_x + j * self.cell_width, matrix_start_y + i * self.cell_height, self.cell_width,
                    self.cell_height), 2)
                if j == opponent_action:
                    pygame.draw.rect(self.screen, (255, 192, 203), (
                    matrix_start_x + j * self.cell_width, matrix_start_y + i * self.cell_height, self.cell_width,
                    self.cell_height), 2)

                payoff = self.font.render(str(matrix[i][j]), True, (0, 0, 0))
                self.screen.blit(payoff, (matrix_start_x + j * self.cell_width, matrix_start_y + i * self.cell_height))

    def close(self):
        pygame.quit()
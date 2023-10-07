import pygame
from SimulationBackbone import FinancialSimulation, Stock  # Assuming the Stock class is also in this file

# Initialize pygame
pygame.init()

# Colors and Screen dimensions
WHITE, GREEN, RED, BLACK = (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0)
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Setup fonts
font = pygame.font.SysFont(None, 36)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Financial Simulator')
        self.simulation = FinancialSimulation(initial_money=1000)

    def draw_text(self, text, color, x, y):
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update the financial simulation
            self.simulation.simulate_period()

            # Drawing
            self.screen.fill(WHITE)

            # Display savings
            self.draw_text(f"Savings: ${self.simulation.money:.2f}", BLACK, 50, 50)

            # Display stock information
            y_offset = 160
            for stock in self.simulation.stocks:
                self.draw_text(f"Stock Name: {stock.name}", BLACK, 50, y_offset)
                self.draw_text(f"Investment Amount: ${stock.invested:.2f}", BLACK, 50, y_offset + 40)
                self.draw_text(f"Price per Stock: ${stock.price:.2f}", BLACK, 50, y_offset + 80)

                gain = (stock.invested / (self.simulation.money + stock.invested)) * 100 - 100
                color = GREEN if gain >= 0 else RED

                self.draw_text(f"Financial Gain: ${gain:.2f}$ ({gain:.2f}%)", color, 50, y_offset + 120)
                y_offset += 200

            pygame.display.flip()
            pygame.time.wait(10)  # Wait for 100ms before updating again

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
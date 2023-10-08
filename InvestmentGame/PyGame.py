import pygame
from SimulationBackbone import FinancialSimulation

# At the beginning of your game file, add:
from utils.data_fetcher import DataFetcher
from utils.data_prepper import DataPrepper

from argparse import ArgumentParser

parser = ArgumentParser()

parser.add_argument("--period_length", type=int, default=255, help="Number of trading days in a year")

args = parser.parse_args()

# Before the Game class definition:
data_fetcher = DataFetcher()
data_fetcher.run()

data_prepper = DataPrepper(args.period_length)
data_prepper.run()


# Initialize pygame
pygame.init()

# Colors
BG_COLOR = (240, 240, 240)  # New background color: very light grey
WHITE, GREEN, RED, BLACK, LIGHT_BLUE, VERY_LIGHT_BLUE, MID_GRAY, LIGHT_GRAY = (255, 255, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0), (173, 216, 230), (225, 240, 255), (169, 169, 169), (220, 220, 220)

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 600
font = pygame.font.SysFont(None, 20)
bold_font = pygame.font.SysFont(None, 20, bold=True)


class TopBar:
    def __init__(self, simulation, screen, game):  # <- Add game here
        self.simulation = simulation
        self.screen = screen
        self.game = game  # <- Store game instance
        self.height = 40  # Define the height attribute here

    def draw(self):
        pygame.draw.rect(self.screen, MID_GRAY, (0, 0, SCREEN_WIDTH, self.height))
        self._draw_text(f"Time Steps: {self.game.timesteps}", BLACK, 50, 10)  # <- Use game.timesteps here
        self._draw_text(f"Available Cash: ${self.simulation.money:.2f}", BLACK, 200, 10)

    def _draw_text(self, text, color, x, y):
        img = font.render(text, True, color)
        self.screen.blit(img, (x, y))


class StockTable:
    def __init__(self, simulation, screen):
        self.simulation = simulation
        self.screen = screen

        # Constants for cell dimensions
        self.CELL_WIDTH = 120
        self.CELL_HEIGHT = 40

    def draw(self):
        headers = ["Name", "Stock Price", "Investment", "Profit/Loss $", "Mean (Yearly)", "Rolling Mean (Annualized)", "Daily Variance", "Rolling Variance"]

        # Draw headers
        for index, header in enumerate(headers):
            self._draw_cell(header, BLACK, 50 + index * self.CELL_WIDTH, 60, bold=True, bgcolor=MID_GRAY)

        y_offset = 100
        for stock in self.simulation.stocks:
            profit_loss = (stock.price - stock.initial_price) * stock.invested
            columns = [
                stock.name,
                f"${stock.price:.2f}",
                f"${stock.invested:.2f}",
                f"${profit_loss:.2f}" if abs(profit_loss) > 0.01 else "$0.00",
                f"{stock.mean_annual:.2f}%",
                f"{stock.rolling_mean_annualized*100:.2f}%" if stock.rolling_mean_annualized is not None else "N/A",
                f"{stock.daily_variance*100:.2f}%",
                f"{stock.rolling_variance_daily*100:.2f}%" if stock.rolling_variance_daily is not None else "N/A"
            ]

            for index, column in enumerate(columns):
                color = BLACK
                bgcolor = LIGHT_GRAY

                if index == 0:  # Stock name cell
                    bgcolor = VERY_LIGHT_BLUE

                if index == 3:  # Profit/loss cell
                    if abs(profit_loss) < 0.01:
                        color = BLACK
                    elif profit_loss >= 0:
                        color = GREEN
                    else:
                        color = RED

                self._draw_cell(column, color, 50 + index * self.CELL_WIDTH, y_offset, bgcolor=bgcolor)

            y_offset += self.CELL_HEIGHT

        # Drawing grid lines
        self._draw_grid(60)

    def _draw_cell(self, text, color, x, y, bold=False, bgcolor=None):
        """Function to draw cell with text centered."""
        text_img = bold_font.render(text, True, color) if bold else font.render(text, True, color)

        # Change: Draw the background for the entire cell
        if bgcolor:
            pygame.draw.rect(self.screen, bgcolor, (x, y, self.CELL_WIDTH, self.CELL_HEIGHT))

        self.screen.blit(text_img, (x + (self.CELL_WIDTH - text_img.get_width()) // 2,
                                    y + (self.CELL_HEIGHT - text_img.get_height()) // 2))

    def _draw_grid(self, start_row_y):
        """Function to draw grid lines for the table."""
        grid_color = (245, 245, 245)  # Very very light gray, almost white
        for i in range(len(self.simulation.stocks) + 2):
            pygame.draw.line(self.screen, grid_color, (50, start_row_y + i * self.CELL_HEIGHT),
                             (50 + 7 * self.CELL_WIDTH, start_row_y + i * self.CELL_HEIGHT))
        for i in range(7):
            pygame.draw.line(self.screen, grid_color, (50 + i * self.CELL_WIDTH, start_row_y),
                             (50 + i * self.CELL_WIDTH,
                              start_row_y + self.CELL_HEIGHT * (len(self.simulation.stocks) + 1)))

class Game:
    def __init__(self, download=True, prep=True):
        self.period_length = args.period_length
        self.data_fetcher = DataFetcher()
        self.data_prepper = DataPrepper(self.period_length)

        if download and not self.data_fetcher.is_data_fetched():
            self.data_fetcher.run()

        if prep and not self.data_prepper.is_data_prepped():
            self.data_prepper.run()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.fill(BG_COLOR)

        pygame.display.set_caption('InvestmentGame')
        self.simulation = FinancialSimulation(period_length=self.period_length, initial_money=1000, num_stocks=5)
        self.top_bar = TopBar(self.simulation, self.screen, self)  # Pass self as the game instance
        self.stock_table = StockTable(self.simulation, self.screen)
        self.timesteps = 0   # Initialize timesteps here

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # TODO: Handle deposit and withdraw button clicks

            self.timesteps += 1  # Update timesteps here
            self.simulation.simulate_period()
            self.screen.fill(WHITE)

            self.top_bar.draw()
            self.stock_table.draw()

            pygame.display.flip()
            pygame.time.wait(1)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
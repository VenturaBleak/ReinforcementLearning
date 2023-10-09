import pygame
from simulation_backbone import FinancialSimulation

# At the beginning of your game file, add:
from utils.data_fetcher import DataFetcher
from utils.data_prepper import DataPrepper
from utils.data_object import InvestmentData
from interface import TopBar, PortfolioTable, Styling

from argparse import ArgumentParser

# hand pick stocks
selected_tickers = ["MSFT", "IBM", "F", "XOM", "SBUX"]

parser = ArgumentParser()
parser.add_argument("--period_length", type=int, default=252, help="Number of trading days in a year")
args = parser.parse_args()

# Before the Game class definition:
data_fetcher = DataFetcher()
data_fetcher.run()

data_prepper = DataPrepper(args.period_length)
data_prepper.run()
data_obj = InvestmentData("investment_data").load()

# Initialize pygame
pygame.init()

class Game:
    def __init__(self, download=True, prep=True):
        self.period_length = args.period_length
        self.data_fetcher = DataFetcher()
        self.data_prepper = DataPrepper(self.period_length)
        self.styling = Styling()
        self.buttons = []

        if download and not self.data_fetcher.is_data_fetched():
            self.data_fetcher.run()

        if prep and not self.data_prepper.is_data_prepped():
            self.data_prepper.run()

        self.screen = pygame.display.set_mode((self.styling.SCREEN_WIDTH, self.styling.SCREEN_HEIGHT))
        self.screen.fill(self.styling.BG_COLOR)  # Change from WHITE to BG_COLOR

        pygame.display.set_caption('InvestmentGame')
        self.simulation = FinancialSimulation(data_obj=data_obj, period_length=self.period_length,
                                              start_date=data_obj.dates[0], starting_balance=1000,
                                              num_stocks=5, hand_picked_stocks=selected_tickers)
        self.top_bar = TopBar(self.simulation, self.screen, self)  # Pass self as the game instance
        self.stock_table = PortfolioTable(self.simulation, self.screen)
        self.timesteps = 0   # Initialize timesteps here

    def update_buttons(self):
        self.buttons = []
        self.buttons.extend(self.top_bar.buttons)
        self.buttons.extend(self.stock_table.buttons)

    def draw_all(self):
        self.screen.fill(self.styling.LIGHT_GRAY)
        self.top_bar.draw()
        self.stock_table.draw()
        self.update_buttons()
        for button in self.buttons:
            button.perform_check()
            button.draw()

    def run(self):
        running = True

        # Drawing the initial state for timestep 0
        self.draw_all()
        pygame.display.flip()

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button.
                        mouse_pos = pygame.mouse.get_pos()
                        for button in self.buttons:
                            if button.x < mouse_pos[0] < button.x + button.width and button.y < mouse_pos[1] < button.y + button.height:
                                button.click()

            # Updating game logic
            self.timesteps += 1  # Update timesteps
            self.simulation.step()

            # Drawing everything on screen
            self.draw_all()
            pygame.display.flip()
            pygame.time.wait(1)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
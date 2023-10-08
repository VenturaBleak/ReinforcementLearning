import pygame

class Styling:
    """Class to store colors used in the game."""
    # init
    def __init__(self):
        # Display constants
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1200, 600

        # Fonts
        self.font = pygame.font.SysFont(None, 20)
        self.bold_font = pygame.font.SysFont(None, 20, bold=True)

        # Colors
        self.BG_COLOR = (240, 240, 240)  # New background color: very light grey
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        self.LIGHT_BLUE = (173, 216, 230)
        self.VERY_LIGHT_BLUE = (225, 240, 255)
        self.MID_GRAY = (169, 169, 169)
        self.LIGHT_GRAY = (220, 220, 220)

class TopBar:
    def __init__(self, simulation, screen, game):  # <- Add game here
        self.simulation = simulation
        self.screen = screen
        self.game = game  # <- Store game instance
        self.height = 40  # Define the height attribute here
        self.styling = Styling()

    def draw(self):
        pygame.draw.rect(self.screen, self.styling.MID_GRAY, (0, 0, self.styling.SCREEN_WIDTH, self.height))
        self._draw_text(f"Time Steps: {self.game.timesteps}", self.styling.BLACK, 50, 10)  # <- Use game.timesteps here
        self._draw_text(f"Available Cash: ${self.simulation.money:.2f}", self.styling.BLACK, 200, 10)

    def _draw_text(self, text, color, x, y):
        img = self.styling.font.render(text, True, color)
        self.screen.blit(img, (x, y))


class StockTable:
    def __init__(self, simulation, screen):
        self.simulation = simulation
        self.screen = screen
        self.styling = Styling()

        # Constants for cell dimensions
        self.CELL_WIDTH = 120
        self.CELL_HEIGHT = 40

    def draw(self):
        headers = ["Name", "Stock Price", "Investment", "Profit/Loss $", "Mean (Yearly)", "Rolling Mean (Annualized)", "Daily Variance", "Rolling Variance"]

        # Draw headers
        for index, header in enumerate(headers):
            self._draw_cell(header, self.styling.BLACK, 50 + index * self.CELL_WIDTH, 60, bold=True, bgcolor=self.styling.MID_GRAY)

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
                color = self.styling.BLACK
                bgcolor = self.styling.LIGHT_GRAY

                if index == 0:  # Stock name cell
                    bgcolor = self.styling.VERY_LIGHT_BLUE

                if index == 3:  # Profit/loss cell
                    if abs(profit_loss) < 0.01:
                        color = self.styling.BLACK
                    elif profit_loss >= 0:
                        color = self.styling.GREEN
                    else:
                        color = self.styling.RED

                self._draw_cell(column, color, 50 + index * self.CELL_WIDTH, y_offset, bgcolor=bgcolor)

            y_offset += self.CELL_HEIGHT

        # Drawing grid lines
        self._draw_grid(60)

    def _draw_cell(self, text, color, x, y, bold=False, bgcolor=None):
        """Function to draw cell with text centered."""
        text_img = self.styling.bold_font.render(text, True, color) if bold else self.styling.font.render(text, True, color)

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
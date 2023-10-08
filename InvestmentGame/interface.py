import pygame

class Styling:
    """Class to store colors used in the game."""
    # init
    def __init__(self):
        # Display constants
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = 1200, 600
        self.CELL_WIDTH, self.CELL_HEIGHT = 120, 40

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
        self._draw_text(f"Available Cash: ${self.simulation.portfolio.assets[0].balance:.2f}", self.styling.BLACK, 200, 10)

        # Use the same button colors as in StockTable for consistency
        portfolio_deposit_button = Button(50 + 2 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2,
                                          10 + (self.styling.CELL_HEIGHT - 30) // 2,
                                          80, 30, "Deposit", (200, 200, 200), (150, 150, 150),
                                          Styling().font, self.portfolio_deposit_action)

        portfolio_withdraw_button = Button(50 + 3 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2,
                                           10 + (self.styling.CELL_HEIGHT - 30) // 2,
                                           80, 30, "Withdraw", (200, 200, 200), (150, 150, 150),
                                           Styling().font, self.portfolio_withdraw_action)

        portfolio_deposit_button.draw(self.screen)
        portfolio_withdraw_button.draw(self.screen)

    def portfolio_deposit_action(self):
    # Handle deposit logic here
        pass

    def portfolio_withdraw_action(self):
    # Handle withdraw logic here
        pass
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
        # Remove the headers for Deposit and Withdraw
        headers = ["Name", "Ticker", "Stock Price", "Balance", "Profit/Loss"]

        for index, header in enumerate(headers):
            self._draw_cell(header, self.styling.BLACK, 50 + index * self.styling.CELL_WIDTH, 60, bold=True,
                            bgcolor=self.styling.MID_GRAY)

        y_offset = 100

        # Draw FedRate first (assuming it's in your portfolio.assets)
        fedrate = self.simulation.portfolio.assets[0]
        self._draw_fedrate(fedrate, y_offset)
        y_offset += self.styling.CELL_HEIGHT

        # Now draw stocks
        for stock in self.simulation.portfolio.stocks:
            self._draw_stock(stock, y_offset)
            y_offset += self.styling.CELL_HEIGHT

        self._draw_grid(60)

    def _draw_fedrate(self, fedrate, y_offset):
        # Placeholder logic similar to stocks, adjust as needed:
        columns = [
            fedrate.name[:11],
            fedrate.ticker[:10],  # Assuming each stock object has a 'ticker' attribute.
            f"${fedrate.price:.2f}",
            f"${fedrate.balance:.2f}",
            f"${0:.2f}"  # Placeholder profit/loss, adjust as needed.
        ]

        for index, column in enumerate(columns):
            bgcolor = self.styling.LIGHT_GRAY
            if index in [0, 1]:  # Name and Ticker cells
                bgcolor = self.styling.LIGHT_BLUE

            self._draw_cell(column, self.styling.BLACK, 50 + index * self.styling.CELL_WIDTH, y_offset, bgcolor=bgcolor)

        # Place buttons centrally within cells
        deposit_button = Button(50 + 5 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2, y_offset + (self.styling.CELL_HEIGHT - 30) // 2,
                                80, 30, "Deposit", (200, 200, 200), (150, 150, 150), Styling().font, self.deposit_action)
        withdraw_button = Button(50 + 6 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2, y_offset + (self.styling.CELL_HEIGHT - 30) // 2,
                                 80, 30, "Withdraw", (200, 200, 200), (150, 150, 150), Styling().font, self.withdraw_action)
        deposit_button.draw(self.screen)
        withdraw_button.draw(self.screen)

    def _draw_stock(self, stock, y_offset):
        columns = [
            stock.name[:15],
            stock.ticker[:10],  # Assuming each stock object has a 'ticker' attribute.
            f"${stock.price:.2f}",
            f"${stock.balance:.2f}",
            f"${0:.2f}"  # Placeholder profit/loss, adjust as needed.
        ]

        for index, column in enumerate(columns):
            bgcolor = self.styling.LIGHT_GRAY
            if index in [0, 1]:  # Name and Ticker cells
                bgcolor = self.styling.LIGHT_BLUE

            self._draw_cell(column, self.styling.BLACK, 50 + index * self.styling.CELL_WIDTH, y_offset, bgcolor=bgcolor)


        deposit_button = Button(
            50 + 5 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2,
            y_offset + (self.styling.CELL_HEIGHT - 30) // 2,
            80, 30, "Deposit", (200, 200, 200), (150, 150, 150),
            Styling().font, self.deposit_action
        )

        withdraw_button = Button(
            50 + 6 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - 80) // 2,
            y_offset + (self.styling.CELL_HEIGHT - 30) // 2,
            80, 30, "Withdraw", (200, 200, 200), (150, 150, 150),
            Styling().font, self.withdraw_action
        )

        deposit_button.draw(self.screen)
        withdraw_button.draw(self.screen)

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
        for i in range(len(self.simulation.portfolio.stocks) + 2):
            pygame.draw.line(self.screen, grid_color, (50, start_row_y + i * self.CELL_HEIGHT),
                             (50 + 7 * self.CELL_WIDTH, start_row_y + i * self.CELL_HEIGHT))
        for i in range(7):
            pygame.draw.line(self.screen, grid_color, (50 + i * self.CELL_WIDTH, start_row_y),
                             (50 + i * self.CELL_WIDTH,
                              start_row_y + self.CELL_HEIGHT * (len(self.simulation.portfolio.stocks) + 1)))

    def deposit_action(self):
    # Handle deposit logic here
        pass

    def withdraw_action(self):
    # Handle withdraw logic here
        pass

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, font, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.active_color = (0, 255, 0)
        self.font = font
        self.action = action
        self.hovered = False
        self.disabled = False

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            self.hovered = True
        else:
            self.hovered = False

        if self.disabled:
            pygame.draw.rect(screen, self.active_color, (self.x, self.y, self.width, self.height))
        elif self.hovered:
            pygame.draw.rect(screen, self.hover_color, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surf, text_rect)

    def click(self):
        if self.hovered and not self.disabled:
            if self.action:
                self.action()

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

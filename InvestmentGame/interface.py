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
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        self.DEEP_BLUE = (0, 0, 128)
        self.LIGHT_BLUE = (173, 216, 230)
        self.VERY_LIGHT_BLUE = (225, 240, 255)
        self.DARK_GRAY = (105, 105, 105)
        self.MID_GRAY = (169, 169, 169)
        self.LIGHT_GRAY = (220, 220, 220)
        self.VERY_LIGHT_GRAY = (245, 245, 245)

        # Button styles
        self.BUTTON_FONT = self.font  # Button font: Default font
        self.BUTTON_FONT_COLOR = self.BLACK  # Button text color: Black
        self.BUTTON_BG_COLOR = self.LIGHT_GRAY  # Button background color: Light gray
        self.BUTTON_HOVER_COLOR = self.DARK_GRAY  # Button hover color: Very light gray
        self.BUTTON_WIDTH = 80  # Width of the button
        self.BUTTON_HEIGHT = 30  # Height of the button

        # Grid Style
        self.grid_color = self.VERY_LIGHT_GRAY

        # Background Style
        self.BG_COLOR = self.BLACK
        self.TABLE_BG_COLOR = self.LIGHT_BLUE  # Slight grey to distinguish the table from the overall background


class TopBar:
    def __init__(self, simulation, screen, game):  # <- Add game here
        self.simulation = simulation
        self.screen = screen
        self.game = game  # <- Store game instance
        self.height = 40  # Define the height attribute here
        self.styling = Styling()
        self.buttons = []

    def draw(self):
        # Draw a rectangle with a background color for the top bar
        pygame.draw.rect(self.screen, self.styling.MID_GRAY, (0, 0, self.styling.SCREEN_WIDTH, self.height))

        # Draw a rectangle with a background color for the timestep and date
        pygame.draw.rect(self.screen, self.styling.LIGHT_BLUE, (30, 5, 280, 22))

        # Render timesteps in one color (e.g., red) and date in another color (e.g., blue)
        timestep_str = f"Time Steps: {self.game.timesteps}"
        date_str = f"Date: {self.simulation.current_date:%Y-%m-%d}"

        timestep_img = self.styling.font.render(timestep_str, True, self.styling.BLACK)
        date_img = self.styling.font.render(date_str, True, self.styling.BLACK)

        # Draw the timestep and date next to each other
        self.screen.blit(timestep_img, (40, 10))
        self.screen.blit(date_img, (180, 10))  # Adjust this value based on the length of your timestep string

        # Right-align the cash amount with some distance from the "Cash:" string
        cash_label = "Available Cash:"
        cash_label_img = self.styling.bold_font.render(cash_label, True, self.styling.BLACK)
        cash_value = f"{self.simulation.player_balance.balance:.2f}$"
        cash_value_img = self.styling.font.render(cash_value, True, self.styling.BLACK)  # Green color for the cash value

        self.screen.blit(cash_label_img, (400, 12))
        self.screen.blit(cash_value_img, (580, 12))  # This places the cash value a bit to the right of the "Cash:" label. Adjust as needed.

        # Draw the Deposit and Withdraw buttons
        self.buttons = []  # Reset the buttons list
        portfolio_deposit_button = Button(
            self.screen,
            680,
            (self.height - self.styling.BUTTON_HEIGHT) // 2,
            "Deposit",
            self.simulation.player_balance,
            self.styling,
            action=self.simulation.player_balance.deposit_to_portfolio,
            check_func=self.simulation.player_balance.can_deposit_to_portfolio
        )
        portfolio_withdraw_button = Button(
            self.screen,
            780,
            (self.height - self.styling.BUTTON_HEIGHT) // 2,
            "Withdraw",
            self.simulation.player_balance,
            self.styling,
            action=self.simulation.player_balance.withdraw_from_portfolio,
            check_func=self.simulation.player_balance.can_withdraw_from_portfolio
        )
        self.buttons.append(portfolio_deposit_button)
        self.buttons.append(portfolio_withdraw_button)

    def _draw_text(self, text, color, x, y):
        img = self.styling.font.render(text, True, color)
        self.screen.blit(img, (x, y))


class PortfolioTable:
    def __init__(self, simulation, screen):
        self.simulation = simulation
        self.screen = screen
        self.styling = Styling()
        self.buttons = []

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

        # Draw the Portfolio Value as the last row
        self._draw_portfolio_value_row(y_offset + self.styling.CELL_HEIGHT)

        self._draw_grid(60)

    def _draw_fedrate(self, fedrate, y_offset):
        # Placeholder logic similar to stocks, adjust as needed:
        columns = [
            fedrate.name[:14],
            fedrate.ticker[:10],  # Assuming each stock object has a 'ticker' attribute.
            f"{fedrate.price:.2f}%",
            f"${fedrate.balance:.2f}",
            f"${0:.2f}"  # Placeholder profit/loss, adjust as needed.
        ]

        for index, column in enumerate(columns):
            bgcolor = self.styling.LIGHT_GRAY
            if index in [0, 1]:  # Name and Ticker cells
                bgcolor = self.styling.LIGHT_BLUE

            self._draw_cell(column, self.styling.BLACK, 50 + index * self.styling.CELL_WIDTH, y_offset, bgcolor=bgcolor)

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

        # Draw the Deposit and Withdraw buttons
        self.buttons = []  # Reset the buttons list
        deposit_button = Button(
            self.screen,
            50 + 5 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - self.styling.BUTTON_WIDTH) // 2,
            y_offset + (self.styling.CELL_HEIGHT - self.styling.BUTTON_HEIGHT) // 2,
            "Deposit",
            stock,
            self.styling,
            action=stock.deposit,
            check_func=stock.can_deposit
        )
        withdraw_button = Button(
            self.screen,
            50 + 6 * self.styling.CELL_WIDTH + (self.styling.CELL_WIDTH - self.styling.BUTTON_WIDTH) // 2,
            y_offset + (self.styling.CELL_HEIGHT - self.styling.BUTTON_HEIGHT) // 2,
            "Withdraw",
            stock,
            self.styling,
            action=stock.withdraw,
            check_func=stock.can_withdraw
        )
        deposit_button.draw()
        withdraw_button.draw()
        self.buttons.append(deposit_button)
        self.buttons.append(withdraw_button)

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
        grid_color = self.styling.grid_color
        for i in range(len(self.simulation.portfolio.stocks) + 2):  # +2 to account for FedRate and Portfolio Value rows
            pygame.draw.line(self.screen, grid_color, (50, start_row_y + i * self.CELL_HEIGHT),
                             (50 + 7 * self.styling.CELL_WIDTH, start_row_y + i * self.CELL_HEIGHT))

        for i in range(8):  # Changed to 8 to draw the grid line at the end
            pygame.draw.line(self.screen, grid_color, (50 + i * self.styling.CELL_WIDTH, start_row_y),
                             (50 + i * self.styling.CELL_WIDTH,
                              start_row_y + self.CELL_HEIGHT * (
                                      len(self.simulation.portfolio.stocks) + 2)))  # +2 here as well

    def _draw_portfolio_value_row(self, y_offset):
        # Move up the y_offset to reduce the gap before the portfolio value row
        y_offset -= (self.styling.CELL_HEIGHT - 3)  # Reduce the visual blank space by CELL_HEIGHT

        columns = [
            "Portfolio Value",
            " ",
            " ",
            f"${self.simulation.portfolio.balance:.2f}",  # Assuming the portfolio object has a balance attribute
            f"${self.simulation.portfolio.profit_loss:.2f}"  # Assuming the portfolio object has a profit_loss attribute
        ]

        for index, column in enumerate(columns):
            bgcolor = self.styling.TABLE_BG_COLOR if index in [3, 4] else self.styling.MID_GRAY  # Slight grey for balance and profit/loss
            self._draw_cell(column, self.styling.BLACK, 50 + index * self.styling.CELL_WIDTH, y_offset, bgcolor=bgcolor)

class Button:
    """Button Class

    Purpose:
    - Create a button object that can be drawn on the screen.
    - The button can be clicked to perform an action. The action triggers a change in the game state (simulation).
    - If the action is invalid, the button will be disabled to prevent it from being clicked.

    Attributes:
    - x, y: x and y coordinates of the top left corner of the button
    - width, height: width and height of the button
    - text: text to be displayed on the button
    - color: color of the button
    - hover_color: color of the button when the mouse hovers over it
    - font: font of the text on the button
    - hovered: boolean to indicate if the mouse is hovering over the button
    - disabled: boolean to indicate if the button is disabled
    - check_func: function to check if the action is valid or not
    - args, kwargs: arguments and keyword arguments to be passed to the action function
    """
    def __init__(self, screen, x, y, text, asset, styling, action=None, check_func=None, *args, **kwargs):
        self.screen = screen
        self.x = x
        self.y = y
        self.width = styling.BUTTON_WIDTH
        self.height = styling.BUTTON_HEIGHT
        self.text = text
        self.active_color = styling.LIGHT_BLUE
        self.passive_color = styling.BUTTON_BG_COLOR
        self.color = self.passive_color
        self.hover_color = styling.BUTTON_HOVER_COLOR
        self.font = styling.BUTTON_FONT
        self.action = action
        self.disabled = False
        self.asset = asset  # associated asset object (stock or player balance)
        self.check_func = check_func  # function to check if the action is valid
        self.args = args
        self.kwargs = kwargs
        self.changed = True

    def draw(self):
        """Function to draw the button on the screen."""
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        self.screen.blit(text_surf, text_rect)

    def click(self):
        if not self.disabled:
            if self.action:
                self.action(*self.args, **self.kwargs)

    def disable(self):
        self.disabled = True
        self.color = self.passive_color

    def enable(self):
        self.disabled = False
        self.color = self.active_color

    def perform_check(self):
        is_valid = self.check_func(*self.args, **self.kwargs) # error caused by this line
        if is_valid:
            self.enable()
        else:
            self.disable()
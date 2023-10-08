import numpy as np

class Asset:
    def __init__(self, ticker, data_obj, starting_date, starting_balance=0.0):
        """
        :param ticker:
        :param data_obj:
        :param period_length:
        :param start_date:
        :param starting_balance:
        """
        self.current_date = starting_date
        self.data_obj = data_obj
        self.ticker = ticker
        if ticker == "FED":
            self.name = "Federal Funds Rate"
        else:
            self.name = self.data_obj.metadata[self.data_obj.metadata["Symbol"] == ticker]["Security"].values[0]

        self.balance = starting_balance
        self.profit = np.nan
        self.price = np.nan
        self.volume = np.nan

    def step(self, current_date):
        """Steps the asset forward by one timestep.

        :return:
        """
        # Update the current date
        self.current_date = current_date

        # Update the price
        self.price = self.data_obj.query(self.ticker, self.current_date, key="Price")

        # Update the volume
        self.volume = self.data_obj.query(self.ticker, self.current_date, key="Volume")

        # Update the profit
        self.profit = self.balance * self.data_obj.query(self.ticker, self.current_date, key="Timestep Return")

        # Update the balance
        self.balance += self.profit

    def deposit(self, amount):
        """Deposits the given amount into the asset.

        :param amount:
        :return:
        """
        self.balance += amount

    def withdraw(self, amount):
        """Withdraws the given amount from the asset, ensuring it doesn't go negative."""
        if amount <= self.balance:
            self.balance -= amount
        else:
            raise ValueError("Insufficient balance for withdrawal")

class FedRate(Asset):
    """Federal Funds Rate Asset Class

    Purpose:
    - Placeholder for now
    """
    def __init__(self, ticker, data_obj, starting_date, starting_balance=0.0):
        super().__init__(ticker, data_obj, starting_date, starting_balance=0.0)

class PlayerBalance(FedRate):
    """Player's Balance Class - Represents the top bar asset."""
    def __init__(self, ticker, data_obj, starting_date, starting_balance=0.0):
        super().__init__(ticker, data_obj, starting_date, starting_balance=0.0)

    # The deposit and withdraw methods can be overridden if unique logic is needed


class Stock(Asset):
    """Stock Asset Class

    Purpose:
    - Placeholder for now
    """
    def __init__(self, ticker, data_obj, starting_date, starting_balance=0.0):
        super().__init__(ticker, data_obj, starting_date, starting_balance=0.0)

class Portfolio:
    def __init__(self, data_obj, period_length, start_date, starting_balance, num_stocks=5, hand_picked_stocks=None):
        self.current_date = start_date

        # Default asset class is FedRate
        self.assets = [FedRate("FED", data_obj, start_date, 0)]

        # Add selection of stocks to the portfolio
        if hand_picked_stocks is not None:
            self.stocks = [Stock(ticker, data_obj, start_date, 0) for ticker in hand_picked_stocks]
            self.assets.extend(self.stocks)
        else:
            available_tickers = [ticker for ticker in data_obj.tickers if ticker != "FED"]
            selected_tickers = np.random.choice(available_tickers, num_stocks, replace=False)
            self.assets.extend([Stock(ticker, data_obj, start_date, 0) for ticker in selected_tickers])

    def money_market(self):
        """Returns the money market asset (FedRate) in the portfolio."""
        for asset in self.assets:
            if isinstance(asset, FedRate):
                return asset
        return None

    def deposit_to_portfolio(self, amount):
        """Deposits the given amount into the portfolio's money market asset."""
        if self.money_market:
            self.money_market.deposit(amount)

    def withdraw_from_portfolio(self, amount):
        """Withdraws the given amount from the portfolio's money market asset."""
        if self.money_market:
            self.money_market.withdraw(amount)

    def update_total_value(self):
        # ToDo: Implement this
        # sum up the balance of all assets
        pass

    def step(self, current_date):
        """Steps the portfolio forward by one timestep.

        :return:
        """
        self.current_date = current_date
        for asset in self.assets:
            asset.step(self.current_date)

class FinancialSimulation:
    """Financial Simulation Class

    Purpose:
    - Central class that controls in-game simulation: Communicates between the PyGame class and the Portfolio class.
    """
    def __init__(self, data_obj, period_length, start_date, starting_balance=1000, num_stocks=5, hand_picked_stocks=None):
        self.period_length = period_length
        self.date_iter = iter([d for d in data_obj.dates if d >= start_date])  # Start iterating from the given start_date
        self.current_date = next(self.date_iter)
        self.data_obj = data_obj
        self.starting_balance = starting_balance
        self.num_stocks = num_stocks
        self.hand_picked_stocks = hand_picked_stocks
        self.time_step = 0

        # Initialize the portfolio
        self.current_date = next(self.date_iter)
        self.portfolio = Portfolio(self.data_obj, self.period_length, self.current_date, 0, self.num_stocks, self.hand_picked_stocks)
        self.player_balance = PlayerBalance("FED", self.data_obj, self.starting_balance)

    def step(self):
        self.portfolio.step(self.current_date)  # Trigger portfolio to step forward
        self.player_balance.step(self.current_date)  # Trigger player balance to step forward
        try:
            self.current_date = next(self.date_iter)
            self.time_step += 1
            return True
        except StopIteration:
            print("Game over. Last date reached.")
            return False
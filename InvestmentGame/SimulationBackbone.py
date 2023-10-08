import numpy as np


class Asset:
    def __init__(self, ticker, data_obj, period_length, start_date, starting_balance=0.0):
        self.period_length = period_length
        self.data_obj = data_obj
        self.ticker = ticker
        self.is_available_flag = self.is_available(start_date)
        self.purchase_price = None
        self.profit_loss = None

        print(f"Date: {start_date}, Ticker: {self.ticker}, Is Available: {self.is_available_flag}")
        self.price = self.data_obj.query(start_date, self.ticker)[0] if self.is_available_flag else None
        self.prev_price = None

        if ticker == "FED":
            self.name = "Federal Funds Rate"
        else:
            self.name = self.data_obj.metadata[self.data_obj.metadata["Symbol"] == ticker]["Security"].values[0]

        self.balance = starting_balance
        self.daily_returns = np.zeros(self.period_length)  # for one year
        self.cursor = 0

    def is_available(self, date):
        return True # @GPT, this is a placeholder, you should implement this method

    def update_running_window(self, daily_return):
        # update running running window logging
        self.daily_returns[self.cursor] = daily_return

        # TODo: double check this
        self.cursor = (self.cursor + 1) % self.period_length

    def simulate_period(self, date):
        raise NotImplementedError

    def update_profit(self):
        raise NotImplementedError

    # TODo: double check this
    def calculate_annualized_mean(self):
        return (np.mean(self.daily_returns) + 1) ** self.period_length - 1

    # TODo: double check this
    def calculate_daily_variance(self):
        return np.std(self.daily_returns)


class FedRate(Asset):
    def __init__(self, ticker, data_obj, period_length, start_date, starting_balance):
        super().__init__(ticker, data_obj, period_length, start_date, starting_balance)

    def simulate_period(self, date):
        if not self.is_available_flag:
            print(f"{self.name} is not available for trading on {date}.")
            return None

        # Fetch the rate
        self.price = self.data_obj.query(date, self.ticker)[0]
        daily_return = (1 + self.price / 100) ** (1 / self.period_length) - 1

        self.balance = self.balance * (1 + daily_return)

        self.update_profit()

        # update running window logging
        self.update_running_window(daily_return)

        # update is_available_flag
        self.is_available(date)

        return daily_return

        # ToDo: update profit
    def update_profit(self):
        pass

class Stock(Asset):
    def __init__(self, ticker, data_obj, period_length, start_date, starting_balance):
        super().__init__(ticker, data_obj, period_length, start_date, starting_balance)

    def simulate_period(self, date):
        if not self.is_available_flag:
            print(f"{self.name} is not available for trading on {date}.")
            return None

        # calculate daily return
        self.prev_price = self.price
        self.price = self.data_obj.query(date, self.ticker)[0]
        daily_return = (self.price - self.prev_price) / self.prev_price - 1
        self.balance = self.balance * (1 + daily_return)

        # update profit
        self.update_profit()

        # update running window logging
        self.update_running_window(daily_return)

        # update is_available_flag
        self.is_available(date)

        return daily_return

    # ToDo: update profit
    def update_profit(self):
        pass


class Portfolio:
    def __init__(self, data_obj, period_length, start_date, starting_balance, num_stocks=5, hand_picked_stocks=None):
        # Default asset class is FedRate
        self.assets = [FedRate("FED", data_obj, period_length, start_date, starting_balance)]

        if hand_picked_stocks is not None:
            self.stocks = [Stock(ticker, data_obj, period_length, start_date, 0) for ticker in hand_picked_stocks]
            self.assets.extend(self.stocks)
        else:
            available_tickers = [ticker for ticker in data_obj.tickers if ticker != "FED"]
            selected_tickers = np.random.choice(available_tickers, num_stocks, replace=False)
            self.assets.extend([Stock(ticker, data_obj, period_length, start_date) for ticker in selected_tickers])

    @property
    def total_value(self):
        total = sum(asset.valuation() for asset in self.assets if not isinstance(asset, FedRate))
        cash_value = next(asset.valuation() for asset in self.assets if isinstance(asset, FedRate))
        return total - cash_value

    def step(self, current_date):
        for asset in self.assets:
            asset.simulate_period(current_date)


class FinancialSimulation:
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
        self.portfolio = Portfolio(self.data_obj, self.period_length, self.current_date, self.starting_balance, self.num_stocks, self.hand_picked_stocks)

    def simulate_period(self):
        self.portfolio.step(self.current_date)  # Trigger portfolio to step forward
        try:
            self.current_date = next(self.date_iter)
            self.time_step += 1
            return True
        except StopIteration:
            print("Game over. Last date reached.")
            return False


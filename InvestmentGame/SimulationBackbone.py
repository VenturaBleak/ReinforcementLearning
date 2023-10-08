import numpy as np
import random
import string

class NumberGenerator:
    def __init__(self, mean, variance):
        self.mean = mean
        self.variance = variance
        self.rng = np.random.default_rng()
        self.weights = self.rng.normal(self.mean, self.variance)

    def generate(self):
        return np.random.normal(self.mean, self.variance)

class Stock:
    def __init__(self, period_length, is_treasury=False):
        self.period_length = period_length
        self.daily_returns = np.zeros(self.period_length)
        self.cursor = 0

        if is_treasury:
            self.name = 'TRES'
            self.price = 100.0
            self.mean_annual = 0
            self.daily_mean = ((self.mean_annual / 100 + 1) ** (1 / self.period_length) - 1)
            self.daily_variance = 0
            self.variance_annual = 0

            # daily return = (1 + fund_rates["Price"] / 100) ** (1 / self.period_length) - 1
        else:
            self.name = ''.join(random.choices(string.ascii_uppercase, k=4))
            self.price = np.random.normal(1, 1.0)
            self.mean_annual = np.random.uniform(-15, 80)
            self.daily_mean = ((self.mean_annual / 100 + 1) ** (1 / self.period_length) - 1)
            self.daily_variance = abs(self.daily_mean) * np.random.uniform(100, self.period_length) / 100
            self.variance_annual = self.daily_variance * np.sqrt(self.period_length)

        self.invested = 0.0
        self.initial_price = self.price

        # period reached flag is set to false, intially
        self.period_reached = False

    def simulate_period(self):
        random_walk = np.random.normal(self.daily_mean, self.daily_variance)
        new_stock_price = self.price * (1 + random_walk)

        daily_return = (new_stock_price - self.price) / self.price
        self.daily_returns[self.cursor] = daily_return
        self.cursor = (self.cursor + 1) % self.period_length

        if self.cursor == self.period_length - 1:
            self.period_reached = True

        if self.period_reached == False:
            self.rolling_mean_annualized = None
            self.rolling_variance_daily = None
            self.variance_annual = None
        else:
            self.rolling_mean_annualized = (np.mean(self.daily_returns) + 1) ** self.period_length - 1
            self.rolling_variance_daily = np.std(self.daily_returns)
            self.variance_annual = self.rolling_variance_daily * np.sqrt(self.period_length)

        self.invested *= (new_stock_price / self.price)
        self.price = new_stock_price

class FinancialSimulation:
    def __init__(self, period_length, initial_money = 1000, num_stocks=5):
        self.money = initial_money
        self.period_length = period_length
        self.savings_variance = 0.0
        self.stocks = [Stock(period_length=self.period_length, is_treasury=True)] + [Stock(period_length=self.period_length) for _ in range(num_stocks)]

    def deposit(self, amount):
        self.money += amount

    def withdraw(self, amount):
        if amount <= self.money:
            self.money -= amount
        else:
            print("Insufficient funds!")

    def invest_in_stock(self, stock_index, amount):
        if amount <= self.money:
            self.money -= amount
            self.stocks[stock_index].invested += amount
        else:
            print("Insufficient funds!")

    def sell_stock(self, stock_index, amount):
        if amount <= self.stocks[stock_index].invested:
            self.stocks[stock_index].invested -= amount
            self.money += amount
        else:
            print("Insufficient stocks!")

    def simulate_period(self):
        for stock in self.stocks:
            stock.simulate_period()
import numpy as np
import random
import string

class Stock:
    def __init__(self):
        self.name = ''.join(random.choices(string.ascii_uppercase, k=4))  # Generate a 4-letter ticker
        self.price = np.random.uniform(0, 10)
        mean_annual = np.random.uniform(-5, 5)
        self.daily_mean = ((mean_annual / 100 + 1) ** (1/255) - 1) # assuming 255 trading days in a year
        # variance is a percentage of the mean
        self.mean_annual = mean_annual
        self.variance_annual = abs(self.daily_mean) * np.random.uniform(100, 50000) / 100
        self.invested = 0.0

    def simulate_period(self):
        random_walk = np.random.normal(self.daily_mean, self.daily_variance)
        print(f"Stock {self.name} changed by {random_walk:.2f}")
        new_stock_price = self.price * (1 + random_walk)
        self.invested *= (new_stock_price / self.price)
        self.price = new_stock_price

class FinancialSimulation:
    def __init__(self, initial_money, num_stocks=5):
        self.money = initial_money
        self.savings_variance = 0.0
        self.stocks = [Stock() for _ in range(num_stocks)]

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
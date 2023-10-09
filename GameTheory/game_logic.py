import numpy as np

class Game:
    def __init__(self, payoffs):
        self.payoffs = payoffs

    def get_payoff(self, action1, action2):
        return self.payoffs[action1][action2]

import numpy as np

from game_logic import Game

class GameModes:
    def __init__(self):
        self.rock_paper_scissors = Game(np.array([[(0, 0), (-1, 1), (1, -1)],
                                                  [(1, -1), (0, 0), (-1, 1)],
                                                  [(-1, 1), (1, -1), (0, 0)]]))

        self.chicken = Game(np.array([[(0, 0), (-1, 1)],
                                      [(1, -1), (-10, -10)]]))

        # Add other games as required

    def get_game(self, game_type):
        if game_type == "rock_paper_scissors":
            return self.rock_paper_scissors
        elif game_type == "chicken":
            return self.chicken
        # Add other game conditions
        else:
            raise ValueError(f"Game type {game_type} not recognized!")

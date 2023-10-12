import torch
import random
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Strategy:
    def __init__(self, env, strategy_type="sample_from_dict"):
        self.env = env
        self.strategy_type = strategy_type

        self.strategies = ["random", "always_defect", "always_cooperate", "model", "tit_for_tat",
                      "grim_trigger", "pavlov", "jesus", "judas", "sample_from_dict"]
        assert self.strategy_type in self.strategies, f"Strategy type must be one of {self.strategies}"

        self.strategy_probabilities = {
            "random": 0.1,
            "always_defect": 0.1,
            "always_cooperate": 0.1,
            "model": 0.1,
            "tit_for_tat": 0.2,
            "grim_trigger": 0.1,
            "pavlov": 0.1,
            "jesus": 0.1,
            "judas": 0.1
        }
        assert sum(self.strategy_probabilities.values()) == 1, "Probabilities must sum up to 1"

        if self.strategy_type == "sample_from_dict":
            self.strategy_type = random.choices(list(self.strategy_probabilities.keys()),
                                                weights=self.strategy_probabilities.values())[0]

    def select_action(self, observation, agent_num=1, model=None):
        # Tit for Tat strategy
        if self.strategy_type == "tit_for_tat":
            if self.env.current_round == 0:
                return 0  # Cooperate on the first round

            last_opponent_action = self.env.actions_history[self.env.current_round - 1][2 - agent_num]

            print(f"current round{self.env.current_round}")
            print(f"action history{self.env.actions_history}")
            print(f"last opponent action {last_opponent_action}")
            return last_opponent_action

        # Random strategy
        elif self.strategy_type == "random":
            return self.env.action_space.sample()

        # Always defect strategy
        elif self.strategy_type == "always_defect":
            return 1

        # Always cooperate strategy
        elif self.strategy_type == "always_cooperate":
            return 0

        # Model strategy
        elif self.strategy_type == "model" and model:
            with torch.no_grad():
                state = torch.tensor(observation, device=device, dtype=torch.float32).unsqueeze(0)
                return model(state).argmax(dim=1).view(1, 1).squeeze(0).item()

        # Default to random if no strategy matches
        return self.env.action_space.sample()
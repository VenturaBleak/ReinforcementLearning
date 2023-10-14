import torch
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Strategy:
    def __init__(self, env, strategy_type="sample_from_dict"):
        self.env = env
        self.strategy_type = strategy_type

        self.strategy_probabilities = {
            "random": 0.1,
            "always_defect": 0.4,
            "always_cooperate": 0.1,
            "model": 0.1,
            "tit_for_tat": 0.3,
            # Omitted unused strategies
        }
        assert sum(self.strategy_probabilities.values()) == 1, "Probabilities must sum up to 1"

        assert self.strategy_type in self.strategy_probabilities or self.strategy_type == "sample_from_dict", \
            f"Strategy type must be one of {list(self.strategy_probabilities.keys())} or 'sample_from_dict'"

        if self.strategy_type == "sample_from_dict":
            self.sampled_strategy = self.sample_strategy()
        else:
            self.sampled_strategy = self.strategy_type

    def select_action(self, observation, model=None):
        # Extract last opponent action from observation based on current round number
        if self.env.current_round == 0:
            last_opponent_action = None
        else:
            last_opponent_action = observation[self.env.current_round * 2 - 1]

        # Tit for Tat strategy
        if self.sampled_strategy == "tit_for_tat":
            if last_opponent_action is None:
                return 0
            return last_opponent_action

        # Random strategy
        elif self.sampled_strategy == "random":
            return self.env.action_space.sample()

        # Always defect strategy
        elif self.sampled_strategy == "always_defect":
            return 1

        # Always cooperate strategy
        elif self.sampled_strategy == "always_cooperate":
            return 0

        # Model strategy
        elif self.sampled_strategy == "model" and model:
            with torch.no_grad():
                state = torch.tensor(observation, device=device, dtype=torch.float32).unsqueeze(0)
                selected_action = model(state).argmax(dim=1).view(1, 1).squeeze(0).item()
                return selected_action

        # Default to random if no strategy matches
        return self.env.action_space.sample()

    def sample_strategy(self):
        """Function to sample strategy based on the predefined probabilities."""
        return random.choices(list(self.strategy_probabilities.keys()),
                              weights=self.strategy_probabilities.values())[0]
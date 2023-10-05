Reinforcement Learning: Frozen Lake
Overview

This repository contains implementations of both Q-learning (QL) and Deep Q-learning (DeepQL) to solve the Frozen Lake environment from OpenAI's Gym library.
Environment: Frozen Lake

Frozen Lake is a grid-world environment where an agent must navigate from a start position to a goal without falling into holes. The lake is made up of four types of blocks: Start (S), Goal (G), Frozen (F), and Hole (H). The agent must reach the Goal (G) from the Start (S) without falling into a Hole (H). The catch is that the Frozen (F) blocks are slippery, so the agent won't always move in the intended direction.

Frozen Lake

Detailed description of the Frozen Lake environment can be found here.
Code Structure
Files in the Repository:

    frozen_lake_map.pkl: Pre-generated map for the Frozen Lake environment.
    generate_map.py: Script to create and save the map for the Frozen Lake environment.
    model.pth: Saved model weights for the Deep Q-learning neural network.
    model.py: Contains the neural network architecture for Deep Q-learning.
    qtable.pkl: Saved Q-table from Q-learning.
    simulation_QL.py: Script to simulate the agent's behavior on Frozen Lake using Q-learning.
    simulation_deepQL.py: Script to simulate the agent's behavior on Frozen Lake using Deep Q-learning.
    train_QL.py: Script to train the agent on the Frozen Lake environment using Q-learning.
    train_deepQL.py: Script to train the agent on the Frozen Lake environment using Deep Q-learning.
    utils.py: Contains utility functions and classes, such as the PolynomialEpsilonDecay for epsilon decay during training.

How to Run:

    Generate the map:

    bash

python generate_map.py

Train using Q-learning:

bash

python train_QL.py --episodes 1000

Simulate using Q-learning:

bash

python simulation_QL.py --episodes 100

Train using Deep Q-learning:

bash

python train_deepQL.py --episodes 1000

Simulate using Deep Q-learning:

bash

python simulation_deepQL.py --episodes 100

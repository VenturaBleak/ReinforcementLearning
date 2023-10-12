from game_env import GameEnv

NUM_EPISODES = 5  # Play 5 episodes
MAX_ROUNDS_PER_EPISODE = 10  # Each episode has 10 rounds

env = GameEnv("chicken", True, max_rounds=MAX_ROUNDS_PER_EPISODE)

for _ in range(NUM_EPISODES):
    observation = env.reset()
    for _ in range(MAX_ROUNDS_PER_EPISODE):
        action_agent1 = env.action_space.sample()
        action_agent2 = env.action_space.sample()
        observations, rewards, terminated, truncated, info = env.step(action_agent1, action_agent2)
        observation_agent1, observation_agent2 = observations
        reward_agent1, reward_agent2 = rewards
        env.render('human')
        if terminated:
            env.episode_counter += 1  # Increment episode counter after termination
            break
env.close()
from game_env import GameEnv

env = GameEnv("chicken", True)
observation = env.reset()
for _ in range(25):  # Render the environment for 10 steps
    action_agent1 = env.action_space.sample()
    action_agent2 = env.action_space.sample()
    observations, rewards, terminated, truncated, info = env.step(action_agent1, action_agent2)
    observation_agent1, observation_agent2 = observations
    reward_agent1, reward_agent2 = rewards
    env.render('human')
    if terminated:
        break
env.close()
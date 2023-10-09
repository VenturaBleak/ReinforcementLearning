from game_env import GameEnv

env = GameEnv("rock_paper_scissors")
observation = env.reset()
for _ in range(5): # Render the environment for 5 steps
    action = env.action_space.sample()
    observation, reward, terminated, truncated, info = env.step(action)
    env.render('human')
env.close()
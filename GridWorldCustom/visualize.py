import gym
import pygame
from environment import MazeGameEnv

gym.register(
    id='MazeGame-v0',
    entry_point='environment:MazeGameEnv',
    kwargs={'maze': None}
)

maze = [
    ['S', '.', '.', '.'],
    ['.', '#', '.', '#'],
    ['.', '.', '.', '.'],
    ['#', '.', '#', 'G'],
]

env = gym.make('MazeGame-v0', maze=maze)
obs = env.reset()
env.render()

done = False
while not done:
    pygame.event.get()
    action = env.action_space.sample()
    obs, reward, done, _ = env.step(action)
    env.render()
    print('Reward:', reward)
    pygame.time.wait(200)
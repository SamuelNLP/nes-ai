"""
A NEAT run on flappy bird with a saved bird
"""

import logging
import pickle
import random
import time
from datetime import datetime

import numpy as np
from ple import PLE
from ple.games.flappybird import FlappyBird

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

WIDTH, HEIGHT = 288, 512
random.seed(datetime.now())
np.random.seed(int(datetime.now().timestamp()))

display = True
path_ = "runs/flappy_n=500_2021-02-14_00:02:43/iteration=385_max=24768.pickle"

with open(path_, "rb") as handle:
    genetic = pickle.load(handle)

individual = list(sorted(genetic.population, reverse=True))[0]
individual.draw()

for network in sorted(genetic.population)[0:10]:
    network.draw()

play = PLE(
    FlappyBird(width=WIDTH, height=HEIGHT, pipe_gap=100), fps=30, display_screen=display
)
actions = play.getActionSet()
play.init()
play.frame_count = 0

while True:
    if play.game_over():
        play.reset_game()
        break

    state = play.getGameState()
    features = (
        state["player_y"] / HEIGHT,
        state["player_vel"] / 8,
        state["next_pipe_dist_to_player"] / WIDTH,
        state["next_pipe_top_y"] / HEIGHT,
        state["next_pipe_bottom_y"] / HEIGHT,
        state["next_next_pipe_dist_to_player"] / WIDTH,
        state["next_next_pipe_top_y"] / HEIGHT,
        state["next_next_pipe_bottom_y"] / HEIGHT,
    )

    button_result = int(np.round(individual.evaluate(features)))

    play.act(actions[button_result])
    logger.debug(play.getFrameNumber())

    time.sleep(0.025)

"""
Super Mario replay
"""

import logging
import pickle
import time

from nes_py.wrappers import JoypadSpace

from nes_ai.input import MOVEMENT, Button, Joypad, neat_result_to_buttons
from nes_ai.mario.env import SuperMario
from scripts.super_mario.super_mario import (
    BUTTON_THRESHOLD,
    BUTTONS_MAP,
    THRESHOLD_FRAME,
)

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

path_ = "runs/mario_n=300_2021-04-02_01:58:59/iteration=224_max=3175.pickle"

with open(path_, "rb") as handle:
    genetic = pickle.load(handle)

individual = list(sorted(genetic.population, reverse=True))[0]
individual.draw()

mario = SuperMario()
player = Joypad(JoypadSpace(mario, MOVEMENT))

while mario.ram[0x0009] < 100:
    player.press((Button.START,), delay=100)

while True:
    mario.render()

    if mario.is_dying:
        mario.close()
        break

    # play
    features = mario.get_input_array()
    indexes = individual.evaluate(features)
    button_result = neat_result_to_buttons(indexes, BUTTONS_MAP, BUTTON_THRESHOLD)

    logger.debug(indexes)
    logger.debug(button_result)

    if button_result:
        player.press(button_result, delay=THRESHOLD_FRAME, replay=True)
    else:
        player.press((Button.NONE,), delay=0)

    x_mario, _ = mario.get_mario()
    time.sleep(0.03)

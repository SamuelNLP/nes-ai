"""
Test for parallel calls on the nes-py openai environments.
"""

import os
import random
from multiprocessing import Pool

from nes_py.wrappers import JoypadSpace

from nes_ai.input import MOVEMENT, Button, Joypad
from nes_ai.tetris.env import Tetris
from nes_ai.tetris.info import GamePhase

BUTTONS = (Button.LEFT, Button.RIGHT, Button.A, Button.B)


def run(_):
    env = Tetris()

    env.reset()
    player = Joypad(JoypadSpace(env, MOVEMENT))

    fitness = 0

    while True:
        env.render()

        if env.game_phase not in (GamePhase.PLAY, GamePhase.LEVEL_AND_HEIGHT):
            player.press((Button.START,), delay=5)
        elif env.game_phase == GamePhase.LEVEL_AND_HEIGHT:
            player.press((Button.DOWN,), delay=5)
            player.press((Button.RIGHT,), delay=5)
            player.press((Button.RIGHT,), delay=5)
            player.press((Button.RIGHT,), delay=5)
            player.press((Button.RIGHT,), delay=5)
            player.press((Button.START,), delay=5)
        else:
            if not env.piece:
                continue

            if env.field.is_full:
                fitness = env.stats.pieces
                env.close()
                break
            else:
                player.press((random.choice(BUTTONS),))

    return fitness


with Pool(os.cpu_count()) as pool:
    result = pool.map(run, tuple(range(100)))
    print(result)

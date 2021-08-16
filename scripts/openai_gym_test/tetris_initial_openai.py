"""
Simple run of Tetris
"""

import random
import time

from nes_py.wrappers import JoypadSpace

from nes_ai.input import MOVEMENT, Button, Joypad
from nes_ai.tetris.env import Tetris
from nes_ai.tetris.info import GamePhase

# Tetris
TETRIS = Tetris()
TETRIS.reset()
PLAYER = Joypad(JoypadSpace(TETRIS, MOVEMENT))

# button_choices
BUTTONS = (Button.LEFT, Button.RIGHT, Button.A, Button.B)

counter = 0
start = 0.0

while True:
    TETRIS.render()

    if TETRIS.game_phase not in (GamePhase.PLAY, GamePhase.LEVEL_AND_HEIGHT):
        PLAYER.press((Button.START,), delay=5)
    elif TETRIS.game_phase == GamePhase.LEVEL_AND_HEIGHT:
        PLAYER.press((Button.DOWN,), delay=5)
        PLAYER.press((Button.RIGHT,), delay=5)
        PLAYER.press((Button.RIGHT,), delay=5)
        PLAYER.press((Button.RIGHT,), delay=5)
        PLAYER.press((Button.RIGHT,), delay=5)
        PLAYER.press((Button.START,), delay=5)

        start = time.time()
    else:
        if not TETRIS.piece:
            continue

        print(TETRIS.stats)
        print(TETRIS.piece)
        print(TETRIS.field)
        print("\n")
        print(TETRIS.field.array_with_piece(TETRIS.piece))

        if TETRIS.field.is_full:
            TETRIS.reset()
            PLAYER.press((Button.NONE,), delay=5)

            print(f"Elapsed: {time.time() - start} seconds.")

            if counter == 5:
                TETRIS.close()
                break

            counter += 1
        else:
            # random right and left
            PLAYER.press((random.choice(BUTTONS),))
            PLAYER.press((Button.DOWN,), delay=0)

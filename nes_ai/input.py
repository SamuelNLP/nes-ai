"""
A representation of a joypad
"""

from enum import Enum
from itertools import combinations
from typing import Dict, Sequence, Tuple

from nes_py.wrappers import JoypadSpace

# possible movements
VALUES = ["left", "right", "A", "B", "down", "NOOP"]
VALUES_TO_COMBINE = VALUES[:-1]

MOVEMENT = [["NOOP"], ["A"], ["B"], ["right"], ["left"], ["down"], ["start"]]

for combine in range(2, 6):
    MOVEMENT += [list(values) for values in combinations(VALUES_TO_COMBINE, combine)]

BUTTON_DELAY = 2  # steps


class Button(Enum):
    """
    Possible buttons
    """

    A = "A"
    B = "B"
    DOWN = "down"
    RIGHT = "right"
    UP = "up"
    LEFT = "left"
    SELECT = "select"
    START = "start"
    NONE = "NOOP"


class Joypad:
    BUTTON_DICT = {
        tuple([Button(name) for name in values]): index
        for index, values in enumerate(MOVEMENT)
    }

    NONE_PRESS = BUTTON_DICT[(Button.NONE,)]

    def __init__(self, env: JoypadSpace):
        self._env = env

    def press(
        self,
        buttons: Tuple[Button, ...],
        delay: int = BUTTON_DELAY,
        replay: bool = False,
    ):
        press_button = self.BUTTON_DICT[buttons]
        self._env.step(press_button)

        for _ in range(delay):
            self._env.step(press_button if replay else self.NONE_PRESS)


def neat_result_to_buttons(
    result: Sequence[float], buttons_map: Dict[int, Button], threshold: float
) -> Tuple[Button, ...]:
    """
    Converts the neats output to list of buttons to press
    """
    indexes = [idx for idx, value in enumerate(result) if value > threshold]
    buttons = [buttons_map[idx] for idx in sorted(indexes)]

    return tuple(buttons)

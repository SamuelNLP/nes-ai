"""
Super Mario Bros represented as an openai nes environment.
"""

import math
from pathlib import Path
from typing import List, Tuple

from nes_ai.env import BaseEnv

RANGE_RADIUS = 16
BOX_RADIUS = 6


class SuperMario(BaseEnv):
    """
    A class that makes a custom NesEnv for super mario.
    """

    def __init__(self):
        super().__init__(str(Path(__file__).parents[1] / "roms" / "super_mario.nes"))
        self.reset()

    @property
    def is_dying(self) -> bool:
        """
        Return True if Mario is in dying animation, False otherwise.
        """
        return self._player_state == 0x0B or self.ram[0x00B5] > 1

    def get_input_array(self) -> List[int]:
        """
        Return a 13 by 13 array:
        """
        mario_x, mario_y = self.get_mario()
        sprites = self._get_stripes()

        inputs = list()
        range_ = range(
            -BOX_RADIUS * RANGE_RADIUS,
            BOX_RADIUS * RANGE_RADIUS + RANGE_RADIUS,
            RANGE_RADIUS,
        )

        for dy in range_:
            for dx in range_:
                input_ = 0

                if (
                    self._get_tile(mario_x, mario_y, dx, dy) == 1
                    and mario_y + dy < 0x1B0
                ):
                    input_ = 1

                for sprite in sprites:
                    dist_x = abs(sprite[0] - (mario_x + dx))
                    dist_y = abs(sprite[1] - (mario_y + dy))
                    if dist_x <= RANGE_RADIUS / 2 and dist_y <= RANGE_RADIUS / 2:
                        input_ = -1

                inputs.append(input_)

        return inputs

    def get_mario(self) -> Tuple[int, ...]:
        """
        Gets Mario position.
        """

        mario_x = self.ram[0x6D] * 0x100 + self.ram[0x86]
        mario_y = self.ram[0x03B8] + RANGE_RADIUS

        return mario_x, mario_y

    def _get_tile(self, mario_x: int, mario_y: int, dx: int, dy: int) -> int:
        x = mario_x + dx + 8
        y = mario_y + dy - RANGE_RADIUS
        page = math.floor(x / 256) % 2

        sub_x = math.floor((x % 256) / RANGE_RADIUS)
        sub_y = math.floor((y - 32) / RANGE_RADIUS)
        addr = 0x500 + page * 13 * RANGE_RADIUS + sub_y * RANGE_RADIUS + sub_x

        if sub_y >= 13 or sub_y < 0:
            return 0

        if self.ram[addr] != 0:
            return 1
        return 0

    def _get_stripes(self) -> List[Tuple[int, int]]:
        sprites = list()

        for slot in range(5):
            enemy = self.ram[0xF + slot]
            if enemy != 0:
                ex = self.ram[0x6E + slot] * 0x100 + self.ram[0x87 + slot]
                ey = self.ram[0xCF + slot] + 24

                sprites.append((ex, ey))

        return sprites

    def _player_state(self) -> int:
        """
        Return the current player state.
        Note:
            0x00 : Leftmost of screen
            0x01 : Climbing vine
            0x02 : Entering reversed-L pipe
            0x03 : Going down a pipe
            0x04 : Auto-walk
            0x05 : Auto-walk
            0x06 : Dead
            0x07 : Entering area
            0x08 : Normal
            0x09 : Cannot move
            0x0B : Dying
            0x0C : Palette cycling, can't move
        """
        return self.ram[0x000E]

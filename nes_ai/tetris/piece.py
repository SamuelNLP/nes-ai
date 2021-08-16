"""
Class and functions that illustrate a Tetris piece
"""

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

import numpy as np


class Piece:
    """
    A piece in tetris

    Parameters
    ----------
    name : str
        Name of the tetris piece, like `T up` for example
    offsets : Sequence of Offset
        Offsets of the piece in a grid like

        For example T up would be like:

        +---------+---------+---------+
        | (-1, 0) | (0,  0) |  (1, 0) |
        +---------+---------+---------+
        |         | (0, -1) |         |
        +---------+---------+---------+

    """

    def __init__(self, name: str, offsets: Sequence["Offset"]):
        self._name = name
        self._offsets = offsets

    @property
    def name(self) -> str:
        return self._name

    @property
    def offsets(self) -> Sequence["Offset"]:
        return self._offsets

    @property
    def offsets_as_tuple(self) -> Tuple[int, ...]:
        list_offsets: List[int] = list()

        for offset in self.offsets:
            list_offsets.extend(offset.as_tuple())

        return tuple(list_offsets)

    @property
    def canvas(self) -> np.ndarray:
        """
        Representation of the offsets in a 5 by 5 canvas, where 1 means the piece
            fills the cell and 0 otherwise

        For example for the T up:

        +---+---+---+---+---+
        | 0 | 0 | 0 | 0 | 0 |
        | 0 | 0 | 0 | 0 | 0 |
        | 0 | 1 | 1 | 1 | 0 |
        | 0 | 0 | 1 | 0 | 0 |
        | 0 | 0 | 0 | 0 | 0 |
        +---+---+---+---+---+
        """
        canvas = np.zeros((5, 5))
        origin = (2, 2)
        canvas[origin] = 1

        for offset in self._offsets:
            canvas[origin[0] + offset.y, origin[1] + offset.x] = 1

        return canvas

    def __str__(self):
        return f"Piece {self._name} \n {np.array2string(self.canvas)}"

    def __repr__(self):
        return f"Piece(name={self._name}, offsets={self._offsets})"

    def __eq__(self, other: object) -> bool:
        if other is self:
            return True

        if not isinstance(other, self.__class__):
            return False

        return other._name == self._name


@dataclass
class Offset:
    y: int
    x: int

    def as_tuple(self):
        return self.x, self.y


def build_pieces() -> Dict[int, Piece]:
    """
    Helper function that build all possible pieces

    Returns
    -------
    dict
        A dict with an hex representation of the piece in the key and a Piece class in
        the value

    """
    return {
        0x00: Piece(name="T up", offsets=(Offset(0, -1), Offset(-1, 0), Offset(0, 1))),
        0x01: Piece(
            name="T right", offsets=(Offset(-1, 0), Offset(1, 0), Offset(0, 1))
        ),
        0x02: Piece(name="T down", offsets=(Offset(0, -1), Offset(1, 0), Offset(0, 1))),
        0x03: Piece(
            name="T left", offsets=(Offset(-1, 0), Offset(1, 0), Offset(0, -1))
        ),
        0x04: Piece(
            name="J left", offsets=(Offset(1, -1), Offset(-1, 0), Offset(1, 0))
        ),
        0x05: Piece(name="J up", offsets=(Offset(0, -1), Offset(-1, -1), Offset(0, 1))),
        0x06: Piece(
            name="J right", offsets=(Offset(-1, 1), Offset(-1, 0), Offset(1, 0))
        ),
        0x07: Piece(name="J down", offsets=(Offset(0, -1), Offset(1, 1), Offset(0, 1))),
        0x08: Piece(
            name="Z horizontal", offsets=(Offset(0, -1), Offset(1, 1), Offset(1, 0))
        ),
        0x09: Piece(
            name="Z vertical", offsets=(Offset(0, 1), Offset(-1, 1), Offset(1, 0))
        ),
        0x0A: Piece(name="O", offsets=(Offset(0, -1), Offset(1, -1), Offset(1, 0))),
        0x0B: Piece(
            name="S horizontal", offsets=(Offset(0, 1), Offset(1, -1), Offset(1, 0))
        ),
        0x0C: Piece(
            name="S vertical", offsets=(Offset(0, 1), Offset(1, 1), Offset(-1, 0))
        ),
        0x0D: Piece(
            name="L right", offsets=(Offset(1, 1), Offset(-1, 0), Offset(1, 0))
        ),
        0x0E: Piece(
            name="L down", offsets=(Offset(0, -1), Offset(1, -1), Offset(0, 1))
        ),
        0x0F: Piece(
            name="L left", offsets=(Offset(-1, -1), Offset(-1, 0), Offset(1, 0))
        ),
        0x10: Piece(name="L up", offsets=(Offset(0, -1), Offset(-1, 1), Offset(0, 1))),
        0x11: Piece(
            name="I vertical", offsets=(Offset(-2, 0), Offset(-1, 0), Offset(1, 0))
        ),
        0x12: Piece(
            name="I horizontal", offsets=(Offset(0, -2), Offset(0, -1), Offset(0, 1))
        ),
    }

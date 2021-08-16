"""
Common info api classes
"""

from dataclasses import dataclass
from enum import Enum, auto


class GamePhase(Enum):
    """
    Phases that a tetris game can have
    """

    LEGAL = auto()
    TITLE = auto()
    GAME_TYPE = auto()
    LEVEL_AND_HEIGHT = auto()
    PLAY = auto()
    DEMO = auto()


class Info(Enum):
    """
    Information that can be requested from the game's RAM
    """

    SCORE = auto()
    LINES = auto()
    PHASE = auto()
    PIECE_X = auto()
    PIECE_Y = auto()
    PIECE_XY = auto()
    PIECE_ID = auto()
    PIECE_ID_NEXT = auto()
    LEVEL_SPEED = auto()
    PIECES = auto()
    FIELD = auto()


@dataclass
class Statistics:
    score: int = 0
    pieces: int = 0
    lines: int = 0
    level: int = 0

    def __str__(self):
        return (
            f"Statistics:\n "
            f"score={self.score}\n "
            f"pieces={self.pieces}\n "
            f"lines={self.lines}\n "
            f"level={self.level}"
        )

    def __repr__(self):
        return (
            f"Statistics("
            f"score={self.score}, "
            f"pieces={self.pieces}, "
            f"lines={self.lines}, "
            f"level={self.level}"
            f")"
        )

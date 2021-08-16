"""
Tetris represented as an openai nes environment.
"""

import random
from pathlib import Path
from typing import Dict, Optional

import numpy as np

from nes_ai.env import BaseEnv
from nes_ai.tetris.field import FIELD_SHAPE, CurrentPiece, Field, Point
from nes_ai.tetris.info import GamePhase, Info, Statistics
from nes_ai.tetris.piece import Piece, build_pieces


class Tetris(BaseEnv):
    """
    A class that makes a custom NesEnv for tetris.
    """

    RAM_INPUT_MAP = {
        Info.SCORE: (0x0053, 0x0054, 0x0055),
        Info.LINES: (0x0050, 0x0051),
        Info.PHASE: 0x00C0,
        Info.PIECE_XY: (0x0040, 0x0041),
        Info.PIECE_ID: 0x0042,
        Info.PIECE_ID_NEXT: 0x0019,
        Info.LEVEL_SPEED: 0x0044,
        Info.PIECES: 0x001A,
        Info.FIELD: range(0x0400, 0x04C7 + 1),
    }

    GAME_PHASE_OUTPUT_MAP = {
        0x00: GamePhase.LEGAL,
        0x01: GamePhase.TITLE,
        0x02: GamePhase.GAME_TYPE,
        0x03: GamePhase.LEVEL_AND_HEIGHT,
        0x04: GamePhase.PLAY,
        0x05: GamePhase.DEMO,
    }

    def __init__(self, pieces: Optional[Dict[int, Piece]] = None):
        super().__init__(str(Path(__file__).parents[1] / "roms" / "tetris.nes"))
        self.reset()
        self._pieces = pieces or build_pieces()

    @property
    def stats(self) -> Statistics:
        return Statistics(
            score=self._read_bytes(Info.SCORE),
            pieces=self._read_byte(Info.PIECES) or 0,
            lines=self._read_bytes(Info.LINES),
            level=self._read_byte(Info.LEVEL_SPEED) or 0,
        )

    @property
    def game_phase(self) -> Optional[GamePhase]:
        if phase := self._read_byte(Info.PHASE):
            return self.GAME_PHASE_OUTPUT_MAP.get(phase)
        return None

    @property
    def piece(self) -> CurrentPiece:
        if piece_address := self._read_byte(Info.PIECE_ID):
            piece = self._pieces.get(piece_address)
            position = self._read_bytes_array(Info.PIECE_XY, big_endian=True)

            return CurrentPiece(
                piece=piece, position=Point(y=position[0], x=position[1])
            )
        return CurrentPiece()

    @property
    def next_piece(self) -> Optional[Piece]:
        if next_piece_address := self._read_byte(Info.PIECE_ID_NEXT):
            return self._pieces.get(next_piece_address)
        return None

    @property
    def field(self) -> Field:
        np_field = np.array(self._read_bytes_array(Info.FIELD, big_endian=False))
        np_field = np.where(np_field == 0xEF, 0, 1)

        return Field(np_field.reshape(FIELD_SHAPE))

    def _did_reset(self):
        """Handle any RAM hacking after a reset occurs."""
        # skip frames and seed the random number generator
        seed = random.randint(0, 255), random.randint(0, 255)
        for _ in range(14):
            self.ram[0x0017:0x0019] = seed
            self._frame_advance(0)

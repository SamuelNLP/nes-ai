"""
Class and functions that illustrate a Tetris field
"""

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from nes_ai.tetris.piece import Piece
from nes_ai.util.prerequisites import require

FIELD_SHAPE = (20, 10)


class Field:
    """
    Representation of a Tetris Field as an array
    """

    def __init__(self, array: np.ndarray):
        require(
            array.shape == FIELD_SHAPE,
            f"Field must have shape {FIELD_SHAPE}, got {array.shape}",
        )
        self._array = array

    @property
    def array(self) -> np.ndarray:
        return self._array

    @property
    def is_full(self) -> bool:
        """
        Checks if the field is completed by pieces, or for example where the game ends
            and the field is filled
        """
        return self._array[0].all()

    def __repr__(self):
        return f"Field({self.array})"

    def __eq__(self, other: object) -> bool:
        if other is self:
            return True

        if not isinstance(other, self.__class__):
            return False

        return np.array_equal(self.array, other.array)

    def array_with_piece(self, current_piece: "CurrentPiece") -> np.ndarray:
        """
        Returns an array of the field with the piece overlaid
        """
        grid = np.copy(self.array)

        if (
            current_piece.piece
            and current_piece.position
            and current_piece.position.is_valid
        ):
            position = current_piece.position

            for offset in current_piece.piece.offsets:
                grid[position.y + offset.y, position.x + offset.x] = 1

            grid[position.y, position.x] = 1

        return grid

    def features(self, piece: "CurrentPiece", next_piece: Piece) -> Optional[Tuple]:
        """
        Returns the features to be consumed by the network
        """

        # without pieces
        # heights: 10 features
        heights = (self._array != 0).argmax(axis=0)
        heights[heights == 0] = self._array.shape[0]

        # holes: 10 features
        holes = np.array(
            [
                int(column[heights[index] :].sum(0))
                if heights[index] < self._array.shape[0]
                else 0
                for index, column in enumerate((1 - self._array).T)
            ]
        )

        heights = heights / FIELD_SHAPE[0]
        holes = holes / FIELD_SHAPE[0]

        # max_height: 1 feature
        max_height = max(heights)

        # height difference: 9 features
        height_diff = np.diff(heights)

        # sum_height_diff: 1 feature
        sum_height_diff = sum(height_diff)

        # with pieces
        # features: pieces, offsets: 12 features
        if piece.piece and piece.position:
            offsets = piece.piece.offsets_as_tuple
        else:
            return None

        if next_piece:
            next_offsets = next_piece.offsets_as_tuple
        else:
            next_offsets = (0,) * 6

        # x_position: 1 feature
        x_position = piece.position.x / FIELD_SHAPE[1]

        array_w_piece = self._array_with_piece_down(piece)

        if array_w_piece is None:
            return None

        # heights: 10 features
        heights_w_piece = (array_w_piece != 0).argmax(axis=0)
        heights_w_piece[heights_w_piece == 0] = array_w_piece.shape[0]

        # holes: 10 features
        holes_w_piece = np.array(
            [
                int(column[heights_w_piece[index] :].sum(0))
                if heights_w_piece[index] < array_w_piece.shape[0]
                else 0
                for index, column in enumerate((1 - array_w_piece).T)
            ]
        )

        heights_w_piece = heights_w_piece / FIELD_SHAPE[0]
        holes_w_piece = holes_w_piece / FIELD_SHAPE[0]

        # max_height: 1 feature
        max_height_w_piece = max(heights_w_piece)

        # height difference: 9 features
        height_diff_w_piece = np.diff(heights_w_piece)

        return tuple(
            np.concatenate(
                (
                    heights,
                    holes,
                    height_diff,
                    offsets,
                    next_offsets,
                    [x_position, max_height, max_height_w_piece, sum_height_diff],
                    heights_w_piece,
                    holes_w_piece,
                    height_diff_w_piece,
                )
            )
        )

    def _array_with_piece_down(self, piece: "CurrentPiece") -> Optional[np.ndarray]:
        """
        Simulates the piece in the final position
        """

        if not piece.piece or not piece.position:
            return None

        baseline = np.sum(self.array_with_piece(piece))

        while (
            piece.position.y < FIELD_SHAPE[0] - 1
            and np.sum(self.array_with_piece(piece)) >= baseline
        ):
            piece = CurrentPiece(
                piece.piece, position=Point(piece.position.x, piece.position.y + 1)
            )

        if not piece.position:
            return None

        piece = CurrentPiece(
            piece.piece, position=Point(piece.position.x, piece.position.y - 1)
        )

        return self.array_with_piece(piece)


@dataclass
class Point:
    """
    Representation of a coordinate point in the tetris field
    """

    x: int
    y: int

    @property
    def is_valid(self) -> bool:
        return self.x > 0 and self.y > 0

    @property
    def as_tuple(self) -> Tuple[int, int]:
        return self.x, self.y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


@dataclass
class CurrentPiece:
    # noinspection PyUnresolvedReferences
    """
    Representation of the current piece in the field

    Parameters
    ----------
    piece : Piece or None
        A Piece object.
    position : Point or None
        The position of the piece.

    """

    piece: Optional[Piece] = None
    position: Optional[Point] = None

    def __repr__(self):
        return f"CurrentPiece(piece={self.piece}, position={self.position})"

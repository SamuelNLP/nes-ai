"""
Test class Field and its function
"""

import random

import numpy as np
import pytest

from nes_ai.tetris.field import FIELD_SHAPE, CurrentPiece, Field, Point
from nes_ai.tetris.piece import build_pieces


def test_field_size():
    valid_size_array = np.random.choice((False, True), size=FIELD_SHAPE)
    wrong_size_array = np.random.choice((False, True), size=(5, 10))

    with pytest.raises(ValueError):
        Field(wrong_size_array)

    assert Field(valid_size_array).array.shape == FIELD_SHAPE


def test_current_piece():
    pieces = build_pieces()

    valid_point = Point(1, 2)

    none_current_piece = CurrentPiece()
    current_piece = CurrentPiece(random.choice(tuple(pieces.values())), valid_point)

    assert none_current_piece.piece is None and none_current_piece.position is None
    assert current_piece.piece and current_piece.position.is_valid


def test_laid_down_piece():
    expected_center = (3, 17)

    pieces = build_pieces()
    current_piece = CurrentPiece(pieces[0x00], Point(3, 2))

    array = np.zeros(FIELD_SHAPE)
    array[19, :] = 1
    array[18, 4] = 1

    field = Field(array)

    array_with_piece = field._array_with_piece_down(current_piece)

    assert array_with_piece[expected_center[1], expected_center[0]] == 1

"""Board representation and small board helpers."""

from .constants import EMPTY, INITIAL_BOARD, WHITE_PIECES, BLACK_PIECES


def create_board():
    """Return a mutable copy of the initial chess board."""
    return [list(row) for row in INITIAL_BOARD]


def in_bounds(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def piece_color(piece):
    if piece in WHITE_PIECES:
        return "blanc"
    if piece in BLACK_PIECES:
        return "noir"
    return None


def same_color(first, second):
    return (
        first != EMPTY
        and second != EMPTY
        and piece_color(first) == piece_color(second)
    )


def copy_board(board):
    return [row.copy() for row in board]


def find_king(board, color):
    king = "♔" if color == "blanc" else "♚"
    for row in range(8):
        for col in range(8):
            if board[row][col] == king:
                return row, col
    return None

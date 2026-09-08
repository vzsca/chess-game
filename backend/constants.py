"""Constants used by the chess engine."""

EMPTY = " "
WHITE = "blanc"
BLACK = "noir"

WHITE_PIECES = "♖♘♗♕♔♙"
BLACK_PIECES = "♜♞♝♛♚♟"

INITIAL_BOARD = (
    ("♜", "♞", "♝", "♛", "♚", "♝", "♞", "♜"),
    ("♟",) * 8,
    (EMPTY,) * 8,
    (EMPTY,) * 8,
    (EMPTY,) * 8,
    (EMPTY,) * 8,
    ("♙",) * 8,
    ("♖", "♘", "♗", "♕", "♔", "♗", "♘", "♖"),
)

KNIGHT_OFFSETS = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1))
KING_OFFSETS = tuple(
    (dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)
ROOK_DIRECTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))
BISHOP_DIRECTIONS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
QUEEN_DIRECTIONS = ROOK_DIRECTIONS + BISHOP_DIRECTIONS

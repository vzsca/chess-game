"""Complete state of a chess game and its FIDE rule handling."""

from .board import create_board, piece_color
from .constants import EMPTY, BLACK_PIECES, WHITE_PIECES
from .moves import game_state, is_in_check, legal_moves


PROMOTION_CHOICES = {"queen", "rook", "bishop", "knight"}
COLORS = {"blanc", "noir"}


class ChessGame:
    """State and rule facade used by the frontend."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.board = create_board()
        self.turn = "blanc"
        self.castling = {
            "blanc": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
            "noir": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
        }
        self.en_passant = None
        self.halfmove_clock = 0
        self.position_history = [self.position_key()]
        self.result = None
        self.game_over = False

    def _effective_en_passant(self):
        """Return the EP target only when a legal EP capture actually exists."""
        if self.en_passant is None or not self._valid_square(*self.en_passant):
            return None

        target_row, target_col = self.en_passant
        pawn = "♙" if self.turn == "blanc" else "♟"
        direction = -1 if pawn == "♙" else 1
        source_row = target_row - direction
        if not 0 <= source_row < 8:
            return None

        for source_col in (target_col - 1, target_col + 1):
            if not 0 <= source_col < 8:
                continue
            if self.board[source_row][source_col] != pawn:
                continue
            if (target_row, target_col) in legal_moves(
                self.board, source_row, source_col, self.castling, self.en_passant
            ):
                return self.en_passant
        return None

    def position_key(self):
        """Return the FIDE identity of the current position."""
        board = tuple(tuple(row) for row in self.board)
        rights = tuple(
            (color, data["king_moved"], data["king_rook_moved"], data["queen_rook_moved"])
            for color, data in sorted(self.castling.items())
        )
        return board, self.turn, rights, self._effective_en_passant()

    def _valid_board(self):
        """Validate the basic invariants required by the move engine."""
        if not isinstance(self.board, list) or len(self.board) != 8:
            return False
        if any(not isinstance(row, list) or len(row) != 8 for row in self.board):
            return False
        allowed = set(WHITE_PIECES + BLACK_PIECES + EMPTY)
        if any(piece not in allowed for row in self.board for piece in row):
            return False
        if sum(piece == "♔" for row in self.board for piece in row) != 1:
            return False
        if sum(piece == "♚" for row in self.board for piece in row) != 1:
            return False

        # A pawn can never legally remain on a promotion rank.
        if any(piece in "♙♟" for piece in self.board[0] + self.board[7]):
            return False

        # Two kings may not occupy adjacent squares.
        white_king = next((
            (r, c) for r in range(8) for c in range(8) if self.board[r][c] == "♔"
        ), None)
        black_king = next((
            (r, c) for r in range(8) for c in range(8) if self.board[r][c] == "♚"
        ), None)
        if white_king is None or black_king is None:
            return False
        if max(abs(white_king[0] - black_king[0]), abs(white_king[1] - black_king[1])) <= 1:
            return False

        # A legal game can never have more than eight pawns for one side.
        if sum(piece == "♙" for row in self.board for piece in row) > 8:
            return False
        if sum(piece == "♟" for row in self.board for piece in row) > 8:
            return False
        return True

    def _valid_state(self):
        """Validate externally mutable game-state fields before processing moves."""
        if self.turn not in COLORS or not self._valid_board():
            return False
        if not isinstance(self.castling, dict) or set(self.castling) != COLORS:
            return False
        required = {"king_moved", "king_rook_moved", "queen_rook_moved"}
        for data in self.castling.values():
            if not isinstance(data, dict) or set(data) != required:
                return False
            if not all(isinstance(value, bool) for value in data.values()):
                return False

        if self.en_passant is not None:
            if (
                not isinstance(self.en_passant, tuple)
                or len(self.en_passant) != 2
                or not all(isinstance(value, int) for value in self.en_passant)
                or not self._valid_square(*self.en_passant)
            ):
                return False
            expected_row = 2 if self.turn == "blanc" else 5
            if self.en_passant[0] != expected_row or self.board[self.en_passant[0]][self.en_passant[1]] != EMPTY:
                return False

        if not isinstance(self.halfmove_clock, int) or self.halfmove_clock < 0:
            return False
        if not isinstance(self.position_history, list) or not self.position_history:
            return False
        return True

    def legal_moves(self, row, col):
        if self.game_over or not self._valid_state():
            return []
        if not self._valid_square(row, col):
            return []
        if piece_color(self.board[row][col]) != self.turn:
            return []
        return legal_moves(self.board, row, col, self.castling, self.en_passant)

    def move(self, source, target, promotion="queen"):
        """Apply a legal move and update all game state."""
        if self.game_over or not self._valid_state():
            return False
        if (
            not isinstance(source, (tuple, list))
            or len(source) != 2
            or not all(isinstance(value, int) for value in source)
            or not isinstance(target, (tuple, list))
            or len(target) != 2
            or not all(isinstance(value, int) for value in target)
        ):
            return False

        row, col = source
        target_row, target_col = target
        if not self._valid_square(row, col) or not self._valid_square(target_row, target_col):
            return False
        if target not in self.legal_moves(row, col):
            return False

        piece = self.board[row][col]
        if piece in "♙♟" and target_row in (0, 7) and promotion not in PROMOTION_CHOICES:
            raise ValueError("promotion must be queen, rook, bishop or knight")
        if piece not in WHITE_PIECES + BLACK_PIECES:
            return False

        old_en_passant = self.en_passant
        captured = self.board[target_row][target_col] != EMPTY
        self.en_passant = None

        if (
            piece in "♙♟"
            and target == old_en_passant
            and self.board[target_row][target_col] == EMPTY
        ):
            captured_row = target_row + (1 if piece == "♙" else -1)
            self.board[captured_row][target_col] = EMPTY
            captured = True

        self._update_moved_rights(piece, source)
        self._invalidate_captured_rook(target)
        self.board[target_row][target_col] = piece
        self.board[row][col] = EMPTY

        if piece in "♔♚" and abs(target_col - col) == 2:
            rook_col = 7 if target_col > col else 0
            rook_target = 5 if target_col > col else 3
            rook = self.board[row][rook_col]
            self.board[row][rook_target] = rook
            self.board[row][rook_col] = EMPTY

        if piece in "♙♟" and target_row in (0, 7):
            self.board[target_row][target_col] = self._promotion_piece(piece, promotion)

        if piece == "♙" and row == 6 and target_row == 4:
            self.en_passant = (5, col)
        elif piece == "♟" and row == 1 and target_row == 3:
            self.en_passant = (2, col)

        self.halfmove_clock = 0 if captured or piece in "♙♟" else self.halfmove_clock + 1
        self.turn = "noir" if self.turn == "blanc" else "blanc"
        self.position_history.append(self.position_key())

        self.result = game_state(
            self.board,
            self.turn,
            self.castling,
            self.en_passant,
            self.halfmove_clock,
            self.position_history,
        )
        self.game_over = self.result is not None
        return True

    def can_claim_fifty_move_draw(self):
        return not self.game_over and self._valid_state() and self.halfmove_clock >= 100

    def can_claim_threefold_repetition(self):
        if self.game_over or not self._valid_state():
            return False
        current = self.position_history[-1]
        return sum(position == current for position in self.position_history) >= 3

    def claim_fifty_move_draw(self):
        if not self.can_claim_fifty_move_draw():
            return False
        self.result = "nulle_50_coups"
        self.game_over = True
        return True

    def claim_threefold_repetition(self):
        if not self.can_claim_threefold_repetition():
            return False
        self.result = "nulle_repetition_trois"
        self.game_over = True
        return True

    def _update_moved_rights(self, piece, source):
        row, col = source
        color = piece_color(piece)
        if piece in "♔♚":
            self.castling[color]["king_moved"] = True
        elif piece in "♖♜":
            if col == 0:
                self.castling[color]["queen_rook_moved"] = True
            elif col == 7:
                self.castling[color]["king_rook_moved"] = True

    def _invalidate_captured_rook(self, target):
        rights = {
            (7, 0): ("blanc", "queen_rook_moved"),
            (7, 7): ("blanc", "king_rook_moved"),
            (0, 0): ("noir", "queen_rook_moved"),
            (0, 7): ("noir", "king_rook_moved"),
        }
        if target in rights:
            color, side = rights[target]
            self.castling[color][side] = True

    @staticmethod
    def _promotion_piece(pawn, promotion):
        choices = {
            "queen": ("♕", "♛"),
            "rook": ("♖", "♜"),
            "bishop": ("♗", "♝"),
            "knight": ("♘", "♞"),
        }
        if promotion not in choices:
            raise ValueError("promotion must be queen, rook, bishop or knight")
        return choices[promotion][0 if pawn == "♙" else 1]

    def is_in_check(self):
        if not self._valid_state():
            return False
        return is_in_check(self.board, self.turn)

    @staticmethod
    def _valid_square(row, col):
        return isinstance(row, int) and isinstance(col, int) and 0 <= row < 8 and 0 <= col < 8

import unittest

from backend.board import create_board, piece_color
from backend.moves import is_in_check, legal_moves


class ChessBackendTests(unittest.TestCase):
    def setUp(self):
        self.castling = {
            "blanc": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
            "noir": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
        }

    def test_initial_board(self):
        board = create_board()
        self.assertEqual(len(board), 8)
        self.assertTrue(all(len(row) == 8 for row in board))
        self.assertEqual(piece_color(board[7][4]), "blanc")
        self.assertEqual(piece_color(board[0][4]), "noir")

    def test_initial_pawn_moves(self):
        board = create_board()
        self.assertIn((5, 0), legal_moves(board, 6, 0, self.castling))
        self.assertIn((4, 0), legal_moves(board, 6, 0, self.castling))

    def test_initial_position_not_in_check(self):
        board = create_board()
        self.assertFalse(is_in_check(board, "blanc"))
        self.assertFalse(is_in_check(board, "noir"))


if __name__ == "__main__":
    unittest.main()

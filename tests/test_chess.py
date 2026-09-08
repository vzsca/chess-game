import unittest

from backend.board import create_board
from backend.game import ChessGame
from backend.moves import is_in_check, legal_moves


class BackendTestCase(unittest.TestCase):
    def empty_game(self):
        game = ChessGame()
        game.board = [[" "] * 8 for _ in range(8)]
        game.castling = {
            "blanc": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
            "noir": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
        }
        game.en_passant = None
        game.halfmove_clock = 0
        game.turn = "blanc"
        game.position_history = [game.position_key()]
        game.result = None
        game.game_over = False
        return game

    def test_initial_board_and_basic_moves(self):
        game = ChessGame()
        self.assertEqual(game.board, create_board())
        self.assertIn((4, 0), game.legal_moves(6, 0))
        self.assertIn((5, 0), game.legal_moves(6, 0))
        self.assertIn((5, 0), game.legal_moves(7, 1))
        self.assertIn((5, 2), game.legal_moves(7, 1))

    def test_piece_cannot_capture_king(self):
        game = self.empty_game()
        game.board[7][0] = "♔"
        game.board[0][7] = "♚"
        game.board[1][7] = "♕"
        game.position_history = [game.position_key()]
        self.assertNotIn((0, 7), game.legal_moves(1, 7))

    def test_king_cannot_move_into_check(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][0] = "♚"
        game.board[0][4] = "♜"
        self.assertNotIn((6, 4), game.legal_moves(7, 4))

    def test_castling_kingside_and_queenside(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[7][7] = "♖"
        game.board[7][0] = "♖"
        game.board[0][4] = "♚"
        self.assertIn((7, 6), game.legal_moves(7, 4))
        self.assertIn((7, 2), game.legal_moves(7, 4))

        self.assertTrue(game.move((7, 4), (7, 6)))
        self.assertEqual(game.board[7][6], "♔")
        self.assertEqual(game.board[7][5], "♖")

    def test_castling_right_is_lost_after_rook_moves(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[7][7] = "♖"
        game.board[0][4] = "♚"
        self.assertTrue(game.move((7, 7), (6, 7)))
        game.turn = "blanc"
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_en_passant(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[3][4] = "♙"
        game.board[1][5] = "♟"
        game.turn = "noir"
        game.position_history = [game.position_key()]
        self.assertTrue(game.move((1, 5), (3, 5)))
        self.assertEqual(game.en_passant, (2, 5))
        self.assertIn((2, 5), game.legal_moves(3, 4))
        self.assertTrue(game.move((3, 4), (2, 5)))
        self.assertEqual(game.board[3][5], " ")
        self.assertEqual(game.board[2][5], "♙")

    def test_all_promotion_choices(self):
        expected = {
            "queen": "♕",
            "rook": "♖",
            "bishop": "♗",
            "knight": "♘",
        }
        for choice, piece in expected.items():
            game = self.empty_game()
            game.board[7][4] = "♔"
            game.board[0][4] = "♚"
            game.board[1][0] = "♙"
            self.assertTrue(game.move((1, 0), (0, 0), choice))
            self.assertEqual(game.board[0][0], piece)

    def test_checkmate_and_stalemate(self):
        mate = self.empty_game()
        mate.board[0][0] = "♚"
        mate.board[1][2] = "♔"
        mate.board[2][1] = "♕"
        mate.turn = "noir"
        self.assertTrue(is_in_check(mate.board, "noir"))
        self.assertEqual(mate.result, None)
        self.assertEqual(
            __import__("backend.moves", fromlist=["game_state"]).game_state(
                mate.board, "noir", mate.castling
            ),
            "mat",
        )

        stalemate = self.empty_game()
        stalemate.board[0][0] = "♚"
        stalemate.board[2][1] = "♔"
        stalemate.board[1][2] = "♕"
        stalemate.turn = "noir"
        self.assertFalse(is_in_check(stalemate.board, "noir"))
        self.assertEqual(
            __import__("backend.moves", fromlist=["game_state"]).game_state(
                stalemate.board, "noir", stalemate.castling
            ),
            "pat",
        )

    def test_threefold_is_claimable_not_automatic(self):
        game = ChessGame()
        sequence = [
            ((7, 6), (5, 5)), ((0, 6), (2, 5)),
            ((5, 5), (7, 6)), ((2, 5), (0, 6)),
        ] * 2
        for source, target in sequence:
            self.assertTrue(game.move(source, target))
        self.assertTrue(game.can_claim_threefold_repetition())
        self.assertFalse(game.game_over)
        self.assertTrue(game.claim_threefold_repetition())
        self.assertEqual(game.result, "nulle_repetition_trois")

    def test_fifty_move_is_claimable_and_seventy_five_is_automatic(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[7][0] = "♖"
        game.halfmove_clock = 100
        game.position_history = [game.position_key()]
        self.assertTrue(game.can_claim_fifty_move_draw())
        self.assertFalse(game.game_over)
        self.assertTrue(game.claim_fifty_move_draw())
        self.assertEqual(game.result, "nulle_50_coups")

        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[7][0] = "♖"
        game.halfmove_clock = 150
        game.position_history = [game.position_key()]
        from backend.moves import game_state
        self.assertEqual(game_state(game.board, game.turn, game.castling, halfmove_clock=150, history=game.position_history), "nulle_75_coups")

    def test_dead_material(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[6][2] = "♗"
        game.position_history = [game.position_key()]
        from backend.moves import game_state
        self.assertEqual(game_state(game.board, game.turn, game.castling, history=game.position_history), "nulle_materiel")

    def test_effective_en_passant_for_repetition_identity(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[3][4] = "♙"
        game.board[1][5] = "♟"
        game.turn = "noir"
        game.en_passant = (2, 5)
        # White's pawn is pinned by the black rook, so the EP capture is not legal.
        game.board[0][5] = "♜"
        self.assertIsNone(game._effective_en_passant())


if __name__ == "__main__":
    unittest.main()

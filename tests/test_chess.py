import unittest

from backend.board import create_board
from backend.game import ChessGame
from backend.moves import game_state, is_in_check


class BackendTestCase(unittest.TestCase):
    def empty_game(self):
        game = ChessGame()
        game.board = [[" " for _ in range(8)] for _ in range(8)]
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.turn = "blanc"
        game.castling = {
            "blanc": {"king_moved": True, "king_rook_moved": True, "queen_rook_moved": True},
            "noir": {"king_moved": True, "king_rook_moved": True, "queen_rook_moved": True},
        }
        game.en_passant = None
        game.halfmove_clock = 0
        game.position_history = [game.position_key()]
        game.result = None
        game.game_over = False
        return game

    def test_initial_board(self):
        game = ChessGame()
        self.assertEqual(game.board, create_board())
        self.assertEqual(game.turn, "blanc")
        self.assertIn((5, 0), game.legal_moves(6, 0))
        self.assertIn((4, 0), game.legal_moves(6, 0))

    def test_initial_pawn_moves(self):
        game = ChessGame()
        self.assertEqual(game.move((6, 4), (4, 4)), True)
        self.assertEqual(game.board[4][4], "♙")
        self.assertEqual(game.turn, "noir")

    def test_invalid_coordinates_and_move_shapes_are_rejected(self):
        game = ChessGame()
        self.assertEqual(game.legal_moves(-1, 0), [])
        self.assertEqual(game.legal_moves(8, 0), [])
        self.assertEqual(game.legal_moves("6", 0), [])
        self.assertFalse(game.move((6, 0), (8, 0)))
        self.assertFalse(game.move((6, 0), (5,)))
        self.assertFalse(game.move("a2", (5, 0)))

    def test_invalid_external_state_is_rejected(self):
        game = ChessGame()
        game.board[0] = []
        self.assertEqual(game.legal_moves(6, 0), [])
        self.assertFalse(game.move((6, 0), (5, 0)))

    def test_invalid_piece_and_missing_king_are_rejected(self):
        game = ChessGame()
        game.board[6][0] = "X"
        self.assertEqual(game.legal_moves(6, 0), [])

        game = ChessGame()
        game.board[7][4] = " "
        self.assertEqual(game.legal_moves(6, 0), [])

    def test_pawn_on_back_rank_is_rejected(self):
        game = ChessGame()
        game.board[0][0] = "♙"
        self.assertEqual(game.legal_moves(6, 0), [])
        self.assertFalse(game.move((6, 0), (5, 0)))

    def test_cannot_capture_king(self):
        game = self.empty_game()
        game.board[7][0] = "♖"
        game.board[0][0] = "♚"
        game.turn = "blanc"
        self.assertNotIn((0, 0), game.legal_moves(7, 0))

    def test_king_cannot_move_into_check(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♜"
        game.board[0][0] = "♚"
        self.assertNotIn((6, 4), game.legal_moves(7, 4))

    def test_castling_kingside_and_queenside(self):
        game = self.empty_game()
        game.board[7][7] = "♖"
        game.board[7][0] = "♖"
        game.castling["blanc"] = {
            "king_moved": False,
            "king_rook_moved": False,
            "queen_rook_moved": False,
        }
        moves = game.legal_moves(7, 4)
        self.assertIn((7, 6), moves)
        self.assertIn((7, 2), moves)

    def test_castling_through_check_is_forbidden(self):
        game = self.empty_game()
        game.board[7][7] = "♖"
        game.castling["blanc"] = {
            "king_moved": False,
            "king_rook_moved": False,
            "queen_rook_moved": True,
        }
        game.board[0][5] = "♜"
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_castling_while_in_check_is_forbidden(self):
        game = self.empty_game()
        game.board[7][7] = "♖"
        game.castling["blanc"] = {
            "king_moved": False,
            "king_rook_moved": False,
            "queen_rook_moved": True,
        }
        game.board[0][4] = "♜"
        game.board[0][0] = "♚"
        self.assertTrue(is_in_check(game.board, "blanc"))
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_castling_right_is_lost_after_rook_moves(self):
        game = ChessGame()
        game.board[7][6] = " "
        game.board[7][5] = " "
        game.board[6][7] = " "
        self.assertTrue(game.move((7, 7), (6, 7)))
        self.assertTrue(game.move((0, 6), (2, 5)))
        self.assertTrue(game.move((6, 7), (7, 7)))
        self.assertTrue(game.castling["blanc"]["king_rook_moved"])

    def test_castling_right_is_lost_after_rook_is_captured(self):
        game = self.empty_game()
        game.board[7][7] = "♖"
        game.board[0][7] = "♜"
        game.board[6][7] = " "
        game.castling["blanc"] = {
            "king_moved": False,
            "king_rook_moved": False,
            "queen_rook_moved": True,
        }
        game.castling["noir"] = {
            "king_moved": True,
            "king_rook_moved": True,
            "queen_rook_moved": True,
        }
        game.turn = "noir"
        self.assertTrue(game.move((0, 7), (7, 7)))
        self.assertTrue(game.castling["blanc"]["king_rook_moved"])

    def test_pawn_double_move_requires_clear_intermediate_square(self):
        game = ChessGame()
        game.board[5][4] = "♟"
        self.assertNotIn((4, 4), game.legal_moves(6, 4))

    def test_en_passant(self):
        game = self.empty_game()
        game.board[3][4] = "♙"
        game.board[1][3] = "♟"
        game.turn = "noir"
        self.assertTrue(game.move((1, 3), (3, 3)))
        game.turn = "blanc"
        self.assertIn((2, 3), game.legal_moves(3, 4))
        self.assertTrue(game.move((3, 4), (2, 3)))
        self.assertEqual(game.board[3][3], " ")

    def test_en_passant_is_only_available_immediately(self):
        game = self.empty_game()
        game.board[3][4] = "♙"
        game.board[1][3] = "♟"
        game.turn = "noir"
        self.assertTrue(game.move((1, 3), (3, 3)))
        game.turn = "blanc"
        self.assertTrue(game.move((7, 4), (7, 5)))
        game.turn = "noir"
        self.assertTrue(game.move((0, 4), (0, 5)))
        game.turn = "blanc"
        self.assertNotIn((2, 3), game.legal_moves(3, 4))

    def test_en_passant_is_illegal_when_it_exposes_king(self):
        game = self.empty_game()
        game.board[3][4] = "♙"
        game.board[1][5] = "♟"
        game.board[0][4] = "♚"
        game.board[0][7] = "♜"
        game.board[7][4] = "♔"
        game.board[6][4] = "♙"
        game.board[1][4] = "♟"
        game.en_passant = (2, 5)
        game.turn = "blanc"
        self.assertNotIn((2, 5), game.legal_moves(3, 4))

    def test_all_white_and_black_promotion_choices(self):
        for promotion in ("queen", "rook", "bishop", "knight"):
            game = self.empty_game()
            game.board[1][0] = "♙"
            game.turn = "blanc"
            self.assertTrue(game.move((1, 0), (0, 0), promotion))

            game = self.empty_game()
            game.board[6][0] = "♟"
            game.turn = "noir"
            self.assertTrue(game.move((6, 0), (7, 0), promotion))

    def test_invalid_promotion_choice_is_rejected(self):
        game = self.empty_game()
        game.board[1][0] = "♙"
        with self.assertRaises(ValueError):
            game.move((1, 0), (0, 0), "king")

    def test_checkmate_and_stalemate(self):
        game = self.empty_game()
        game.board[7][4] = " "
        game.board[0][0] = "♚"
        game.board[5][2] = "♔"
        game.board[1][1] = "♕"
        game.turn = "noir"
        self.assertEqual(game_state(game.board, game.turn, game.castling), "mat")

        game = self.empty_game()
        game.board[7][4] = " "
        game.board[0][0] = "♚"
        game.board[5][2] = "♔"
        game.board[2][1] = "♕"
        game.turn = "noir"
        self.assertEqual(game_state(game.board, game.turn, game.castling), "pat")

    def test_threefold_repetition_is_claimable_not_automatic(self):
        game = self.empty_game()
        game.board[7][0] = "♖"
        game.position_history = [game.position_key()] * 3
        self.assertIsNone(game_state(game.board, game.turn, game.castling, history=game.position_history))
        self.assertTrue(game.can_claim_threefold_repetition())

    def test_fivefold_repetition_is_automatic(self):
        game = self.empty_game()
        game.board[7][0] = "♖"
        game.position_history = [game.position_key()] * 5
        self.assertEqual(game_state(game.board, game.turn, game.castling, history=game.position_history), "nulle_repetition_cinq")

    def test_fifty_move_rule_is_claimable_and_seventy_five_is_automatic(self):
        game = self.empty_game()
        game.board[7][0] = "♖"
        game.halfmove_clock = 100
        self.assertTrue(game.can_claim_fifty_move_draw())
        self.assertIsNone(game_state(game.board, game.turn, game.castling, halfmove_clock=100))
        game.halfmove_clock = 150
        self.assertEqual(game_state(game.board, game.turn, game.castling, halfmove_clock=150), "nulle_75_coups")

    def test_checkmate_takes_precedence_over_seventy_five_move_draw(self):
        game = self.empty_game()
        game.board[7][4] = " "
        game.board[0][0] = "♚"
        game.board[5][2] = "♔"
        game.board[1][1] = "♕"
        game.turn = "noir"
        game.halfmove_clock = 150
        self.assertEqual(game_state(game.board, game.turn, game.castling, halfmove_clock=150), "mat")

    def test_dead_material(self):
        game = self.empty_game()
        game.board[7][2] = "♗"
        self.assertEqual(
            game_state(game.board, game.turn, game.castling, history=game.position_history),
            "nulle_materiel",
        )

    def test_same_color_bishops_are_dead(self):
        game = self.empty_game()
        game.board[7][2] = "♗"
        game.board[1][2] = "♝"
        game.position_history = [game.position_key()]
        self.assertEqual(
            game_state(game.board, game.turn, game.castling, history=game.position_history),
            "nulle_materiel",
        )

    def test_opposite_color_bishops_are_not_declared_dead(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[7][2] = "♗"
        game.board[1][1] = "♝"
        game.position_history = [game.position_key()]
        self.assertNotEqual(
            game_state(game.board, game.turn, game.castling, history=game.position_history),
            "nulle_materiel",
        )

    def test_effective_en_passant_for_repetition_identity(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][0] = "♚"
        game.board[3][4] = "♙"
        game.en_passant = (2, 3)
        with_ep = game.position_key()
        game.en_passant = None
        without_ep = game.position_key()
        self.assertEqual(with_ep, without_ep)

        game.board[3][3] = "♟"
        game.en_passant = (2, 3)
        with_effective_ep = game.position_key()
        game.en_passant = None
        without_effective_ep = game.position_key()
        self.assertNotEqual(with_effective_ep, without_effective_ep)

    def test_game_cannot_be_played_after_terminal_state(self):
        game = self.empty_game()
        game.board[0][0] = "♚"
        game.board[2][2] = "♔"
        game.board[1][1] = "♕"
        game.turn = "noir"
        game.result = "mat"
        game.game_over = True
        self.assertFalse(game.move((0, 0), (1, 0)))


if __name__ == "__main__":
    unittest.main()

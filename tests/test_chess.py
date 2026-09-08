import unittest

from backend.board import create_board
from backend.game import ChessGame
from backend.moves import game_state, is_in_check


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

    def test_invalid_coordinates_and_move_shapes_are_rejected(self):
        game = ChessGame()
        for square in [(-1, 0), (8, 0), (0, 8), (0, -1), ("0", 0), (0, None)]:
            self.assertEqual(game.legal_moves(*square), [])
        self.assertFalse(game.move((-1, 0), (5, 0)))
        self.assertFalse(game.move((6, 0), (8, 0)))
        self.assertFalse(game.move("bad", (5, 0)))
        self.assertFalse(game.move((6, 0), "bad"))

    def test_invalid_external_state_is_rejected_without_mutation(self):
        game = ChessGame()
        original = [row.copy() for row in game.board]
        game.board = [[" "] * 7 for _ in range(8)]
        self.assertEqual(game.legal_moves(6, 0), [])
        self.assertFalse(game.move((6, 0), (5, 0)))
        self.assertEqual(game.board, [[" "] * 7 for _ in range(8)])

        game.board = original
        game.turn = "invalid"
        self.assertEqual(game.legal_moves(6, 0), [])
        self.assertFalse(game.move((6, 0), (5, 0)))

    def test_invalid_piece_and_missing_king_are_rejected(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[3][3] = "X"
        self.assertEqual(game.legal_moves(3, 3), [])
        game.board[0][4] = " "
        self.assertEqual(game.legal_moves(7, 4), [])

    def test_pawns_cannot_start_on_back_rank(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[0][0] = "♙"
        self.assertEqual(game.legal_moves(0, 0), [])
        self.assertFalse(game.move((0, 0), (1, 0)))

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

    def test_castling_is_forbidden_through_check(self):
        for attacked_square in (5, 6):
            game = self.empty_game()
            game.board[7][4] = "♔"
            game.board[7][7] = "♖"
            game.board[0][4] = "♚"
            game.board[0][attacked_square] = "♜"
            self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_castling_is_forbidden_while_in_check(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[7][7] = "♖"
        game.board[0][4] = "♚"
        game.board[0][4] = "♜"
        game.board[0][0] = "♚"
        self.assertTrue(is_in_check(game.board, "blanc"))
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_castling_right_is_lost_after_rook_moves(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[7][7] = "♖"
        game.board[0][4] = "♚"
        self.assertTrue(game.move((7, 7), (6, 7)))
        game.turn = "blanc"
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_capturing_original_rook_removes_castling_right(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[7][7] = "♖"
        game.board[0][4] = "♚"
        game.board[0][7] = "♜"
        game.turn = "noir"
        self.assertTrue(game.move((0, 7), (7, 7)))
        game.turn = "blanc"
        self.assertNotIn((7, 6), game.legal_moves(7, 4))

    def test_pawn_double_move_requires_clear_intermediate_square(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[6][0] = "♙"
        game.board[5][0] = "♟"
        self.assertNotIn((4, 0), game.legal_moves(6, 0))

    def test_en_passant(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[3][4] = "♙"
        game.board[1][3] = "♟"
        game.turn = "noir"
        game.position_history = [game.position_key()]
        self.assertTrue(game.move((1, 3), (3, 3)))
        self.assertEqual(game.en_passant, (2, 3))
        self.assertIn((2, 3), game.legal_moves(3, 4))
        self.assertTrue(game.move((3, 4), (2, 3)))
        self.assertEqual(game.board[3][3], " ")
        self.assertEqual(game.board[2][3], "♙")

    def test_en_passant_is_only_available_immediately(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[3][4] = "♙"
        game.board[1][3] = "♟"
        game.turn = "noir"
        self.assertTrue(game.move((1, 3), (3, 3)))
        game.turn = "noir"
        game.en_passant = None
        self.assertNotIn((2, 3), game.legal_moves(3, 4))

    def test_en_passant_is_illegal_when_it_exposes_king(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][0] = "♚"
        game.board[0][4] = "♜"
        game.board[3][4] = "♙"
        game.board[3][5] = "♟"
        game.turn = "blanc"
        game.en_passant = (2, 5)
        self.assertNotIn((2, 5), game.legal_moves(3, 4))

    def test_all_white_and_black_promotion_choices(self):
        choices = {
            "queen": ("♕", "♛"),
            "rook": ("♖", "♜"),
            "bishop": ("♗", "♝"),
            "knight": ("♘", "♞"),
        }
        for choice, pieces in choices.items():
            game = self.empty_game()
            game.board[7][4] = "♔"
            game.board[0][4] = "♚"
            game.board[1][0] = "♙"
            self.assertTrue(game.move((1, 0), (0, 0), choice))
            self.assertEqual(game.board[0][0], pieces[0])

            game = self.empty_game()
            game.board[7][4] = "♔"
            game.board[0][4] = "♚"
            game.board[6][0] = "♟"
            game.turn = "noir"
            self.assertTrue(game.move((6, 0), (7, 0), choice))
            self.assertEqual(game.board[7][0], pieces[1])

    def test_invalid_promotion_choice_is_rejected(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[1][0] = "♙"
        with self.assertRaises(ValueError):
            game.move((1, 0), (0, 0), "king")

    def test_checkmate_and_stalemate(self):
        mate = self.empty_game()
        mate.board[0][0] = "♚"
        mate.board[2][2] = "♔"
        mate.board[1][1] = "♕"
        mate.turn = "noir"
        self.assertTrue(is_in_check(mate.board, "noir"))
        self.assertEqual(game_state(mate.board, "noir", mate.castling), "mat")

        stalemate = self.empty_game()
        stalemate.board[0][0] = "♚"
        stalemate.board[2][2] = "♔"
        stalemate.board[2][1] = "♕"
        stalemate.turn = "noir"
        self.assertFalse(is_in_check(stalemate.board, "noir"))
        self.assertEqual(game_state(stalemate.board, "noir", stalemate.castling), "pat")

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

    def test_fivefold_repetition_is_automatic(self):
        game = ChessGame()
        sequence = [
            ((7, 6), (5, 5)), ((0, 6), (2, 5)),
            ((5, 5), (7, 6)), ((2, 5), (0, 6)),
        ] * 4
        for source, target in sequence:
            self.assertTrue(game.move(source, target))
        self.assertTrue(game.game_over)
        self.assertEqual(game.result, "nulle_repetition_cinq")

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
        self.assertEqual(
            game_state(
                game.board,
                game.turn,
                game.castling,
                halfmove_clock=150,
                history=game.position_history,
            ),
            "nulle_75_coups",
        )

    def test_checkmate_takes_precedence_over_seventy_five_move_draw(self):
        game = self.empty_game()
        game.board[0][0] = "♚"
        game.board[2][2] = "♔"
        game.board[1][1] = "♕"
        game.turn = "noir"
        game.halfmove_clock = 150
        self.assertEqual(
            game_state(game.board, game.turn, game.castling, halfmove_clock=150),
            "mat",
        )

    def test_dead_material(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[6][2] = "♗"
        game.position_history = [game.position_key()]
        self.assertEqual(
            game_state(game.board, game.turn, game.castling, history=game.position_history),
            "nulle_materiel",
        )

    def test_same_color_bishops_are_dead_material(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[6][2] = "♗"
        game.board[1][5] = "♝"
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
        game.board[1][2] = "♝"
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
        game.board[3][5] = "♟"
        game.board[0][4] = "♜"
        game.turn = "blanc"
        game.en_passant = (2, 5)
        self.assertIsNone(game._effective_en_passant())

    def test_game_cannot_be_played_after_terminal_state(self):
        game = self.empty_game()
        game.board[7][4] = "♔"
        game.board[0][4] = "♚"
        game.board[7][2] = "♗"
        game.result = "pat"
        game.game_over = True
        before = [row.copy() for row in game.board]
        self.assertFalse(game.move((7, 4), (6, 4)))
        self.assertEqual(game.board, before)


if __name__ == "__main__":
    unittest.main()

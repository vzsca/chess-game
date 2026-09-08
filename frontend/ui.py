"""Tkinter user interface for the chess game."""
from tkinter import Button, DISABLED, Label

from backend.board import create_board, piece_color
from backend.moves import game_state, is_in_check, legal_moves


class ChessUI:
    """Display and control a two-player chess game."""

    def __init__(self, root):
        self.root = root
        self.board = create_board()
        self.castling = {
            "blanc": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
            "noir": {"king_moved": False, "king_rook_moved": False, "queen_rook_moved": False},
        }
        self.turn = "blanc"
        self.selected = None
        self.highlighted = []
        self.buttons = [[None] * 8 for _ in range(8)]
        self.turn_label = Label(root, text="Tour des blancs", font=("Arial", 14))
        self.turn_label.grid(row=8, column=0, columnspan=8)
        self.info_label = Label(root, text="", font=("Arial", 12))
        self.info_label.grid(row=9, column=0, columnspan=8)
        self._create_board()

    @staticmethod
    def _base_color(row, col):
        return "white" if (row + col) % 2 == 0 else "grey"

    def _create_board(self):
        for row in range(8):
            for col in range(8):
                button = Button(self.root, text=self.board[row][col], font=("Arial", 17), width=3, height=1,
                                bg=self._base_color(row, col), command=lambda r=row, c=col: self.on_square_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def refresh(self):
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].config(text=self.board[row][col])

    def clear_highlights(self):
        for row, col in self.highlighted:
            self.buttons[row][col].config(bg=self._base_color(row, col))
        if self.selected:
            row, col = self.selected
            self.buttons[row][col].config(bg=self._base_color(row, col))
        self.highlighted.clear()
        self.selected = None

    def highlight_moves(self, moves):
        for row, col in moves:
            self.buttons[row][col].config(bg="orange" if self.board[row][col] != " " else "green")
        self.highlighted = list(moves)

    def _update_castling_rights(self, piece, source):
        color = piece_color(piece)
        if piece in "♔♚":
            self.castling[color]["king_moved"] = True
        elif piece in "♖♜":
            _, col = source
            if col == 0: self.castling[color]["queen_rook_moved"] = True
            elif col == 7: self.castling[color]["king_rook_moved"] = True

    def _move_piece(self, source, target):
        sr, sc = source; tr, tc = target
        piece = self.board[sr][sc]
        self._update_castling_rights(piece, source)
        self.board[tr][tc] = piece
        self.board[sr][sc] = " "

        if piece in "♔♚" and abs(tc - sc) == 2:
            rc = 7 if tc > sc else 0
            rtc = 5 if tc > sc else 3
            self.board[sr][rtc] = self.board[sr][rc]
            self.board[sr][rc] = " "

        if piece == "♙" and tr == 0: self.board[tr][tc] = "♕"
        elif piece == "♟" and tr == 7: self.board[tr][tc] = "♛"

    def _finish_turn(self):
        self.turn = "noir" if self.turn == "blanc" else "blanc"
        self.turn_label.config(text=f"Tour des {self.turn}s")
        state = game_state(self.board, self.turn, self.castling)
        if state == "mat":
            winner = "noirs" if self.turn == "blanc" else "blancs"
            self.info_label.config(text=f"♛ Échec et mat ! Les {winner} gagnent.")
            self.disable_board()
        elif state == "pat":
            self.info_label.config(text="🤝 Pat ! Match nul.")
            self.disable_board()
        elif is_in_check(self.board, self.turn):
            self.info_label.config(text=f"⚠️ Échec au roi {self.turn} !")
        else:
            self.info_label.config(text="")

    def on_square_click(self, row, col):
        piece = self.board[row][col]
        if self.selected and (row, col) in self.highlighted:
            self._move_piece(self.selected, (row, col))
            self.clear_highlights()
            self.refresh()
            self._finish_turn()
            return
        if piece_color(piece) == self.turn:
            self.clear_highlights()
            self.selected = (row, col)
            self.buttons[row][col].config(bg="red")
            self.highlight_moves(legal_moves(self.board, row, col, self.castling))
        else:
            self.clear_highlights()

    def disable_board(self):
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].config(state=DISABLED)

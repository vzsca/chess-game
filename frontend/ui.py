"""Tkinter user interface for the chess game."""
from tkinter import Button, DISABLED, Label

from backend.board import piece_color
from backend.game import ChessGame


class ChessUI:
    """Display and control a two-player chess game."""

    def __init__(self, root):
        self.root = root
        self.game = ChessGame()
        self.selected = None
        self.highlighted = []
        self.buttons = [[None] * 8 for _ in range(8)]
        self.turn_label = Label(root, text="Tour des blancs", font=("Arial", 14))
        self.turn_label.grid(row=8, column=0, columnspan=8)
        self.info_label = Label(root, text="", font=("Arial", 12))
        self.info_label.grid(row=9, column=0, columnspan=8)
        self._create_board()

    @property
    def board(self):
        return self.game.board

    @staticmethod
    def _base_color(row, col):
        return "white" if (row + col) % 2 == 0 else "grey"

    def _create_board(self):
        for row in range(8):
            for col in range(8):
                button = Button(
                    self.root, text=self.board[row][col], font=("Arial", 17),
                    width=3, height=1, bg=self._base_color(row, col),
                    command=lambda r=row, c=col: self.on_square_click(r, c),
                )
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
            bg = "orange" if self.board[row][col] != " " else "green"
            self.buttons[row][col].config(bg=bg)
        self.highlighted = list(moves)

    def on_square_click(self, row, col):
        piece = self.board[row][col]
        if self.selected and (row, col) in self.highlighted:
            self.game.move(self.selected, (row, col))
            self.clear_highlights()
            self.refresh()
            self._update_status()
            return

        if piece_color(piece) == self.game.turn:
            self.clear_highlights()
            self.selected = (row, col)
            self.buttons[row][col].config(bg="red")
            self.highlight_moves(self.game.legal_moves(row, col))
        else:
            self.clear_highlights()

    def _update_status(self):
        self.turn_label.config(text=f"Tour des {self.game.turn}s")
        messages = {
            "mat": f"♛ Échec et mat ! Les {'noirs' if self.game.turn == 'blanc' else 'blancs'} gagnent.",
            "pat": "🤝 Pat ! Match nul.",
            "nulle_50_coups": "🤝 Nulle : règle des 50 coups.",
            "nulle_repetition": "🤝 Nulle : triple répétition.",
            "nulle_materiel": "🤝 Nulle : matériel insuffisant.",
        }
        if self.game.result in messages:
            self.info_label.config(text=messages[self.game.result])
            self.disable_board()
        elif self.game.is_in_check():
            self.info_label.config(text=f"⚠️ Échec au roi {self.game.turn} !")
        else:
            self.info_label.config(text="")

    def disable_board(self):
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].config(state=DISABLED)

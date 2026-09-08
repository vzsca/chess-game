"""Tkinter user interface for the chess game."""

from tkinter import Button, DISABLED, Label, NORMAL, OptionMenu, StringVar, Toplevel

from backend.board import piece_color
from backend.game import ChessGame


class ChessUI:
    """Display and control a two-player chess game."""

    PROMOTION_LABELS = {
        "queen": "Dame ♕",
        "rook": "Tour ♖",
        "bishop": "Fou ♗",
        "knight": "Cavalier ♘",
    }

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

        self.claim_frame = None
        self.claim_50_button = None
        self.claim_3fold_button = None
        self._create_board()
        self._create_draw_controls()
        self._update_status()

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
                    self.root,
                    text=self.board[row][col],
                    font=("Arial", 17),
                    width=3,
                    height=1,
                    bg=self._base_color(row, col),
                    command=lambda r=row, c=col: self.on_square_click(r, c),
                )
                button.grid(row=row, column=col)
                self.buttons[row][col] = button

    def _create_draw_controls(self):
        self.claim_frame = Label(self.root)
        self.claim_frame.grid(row=10, column=0, columnspan=8)

        self.claim_50_button = Button(
            self.claim_frame,
            text="Réclamer nulle — 50 coups",
            command=self.claim_fifty_move_draw,
            state=DISABLED,
        )
        self.claim_50_button.pack(side="left", padx=3)

        self.claim_3fold_button = Button(
            self.claim_frame,
            text="Réclamer nulle — répétition",
            command=self.claim_threefold_draw,
            state=DISABLED,
        )
        self.claim_3fold_button.pack(side="left", padx=3)

    def refresh(self):
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].config(text=self.board[row][col])

    def clear_highlights(self):
        for row, col in self.highlighted:
            self.buttons[row][col].config(bg=self._base_color(row, col))
        if self.selected is not None:
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
        if self.game.game_over:
            return

        piece = self.board[row][col]
        if self.selected is not None and (row, col) in self.highlighted:
            source = self.selected
            moving_piece = self.board[source[0]][source[1]]
            promotion = self.choose_promotion() if moving_piece in "♙♟" and row in (0, 7) else "queen"
            if promotion is None:
                return

            self.game.move(source, (row, col), promotion)
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

    def choose_promotion(self):
        """Show a modal promotion picker and return the selected piece."""
        popup = Toplevel(self.root)
        popup.title("Promotion")
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        Label(popup, text="Choisissez la pièce de promotion :", font=("Arial", 11)).pack(
            padx=15, pady=(15, 8)
        )

        selected = StringVar(popup, value="queen")
        options = list(self.PROMOTION_LABELS.keys())
        OptionMenu(
            popup,
            selected,
            *options,
        ).pack(padx=15, pady=5)

        result = {"value": None}

        def validate():
            result["value"] = selected.get()
            popup.destroy()

        Button(popup, text="Valider", command=validate).pack(pady=(8, 15))
        popup.protocol("WM_DELETE_WINDOW", popup.destroy)
        popup.wait_window()
        return result["value"]

    def claim_fifty_move_draw(self):
        if self.game.claim_fifty_move_draw():
            self.clear_highlights()
            self._update_status()

    def claim_threefold_draw(self):
        if self.game.claim_threefold_repetition():
            self.clear_highlights()
            self._update_status()

    def _update_status(self):
        self.turn_label.config(text=f"Tour des {self.game.turn}s")
        messages = {
            "mat": f"♛ Échec et mat ! Les {'noirs' if self.game.turn == 'blanc' else 'blancs'} gagnent.",
            "pat": "🤝 Pat ! Match nul.",
            "nulle_50_coups": "🤝 Nulle : règle des 50 coups.",
            "nulle_75_coups": "🤝 Nulle : règle des 75 coups.",
            "nulle_repetition_trois": "🤝 Nulle : triple répétition.",
            "nulle_repetition_cinq": "🤝 Nulle : quintuple répétition.",
            "nulle_materiel": "🤝 Nulle : position morte (matériel insuffisant).",
        }

        if self.game.result in messages:
            self.info_label.config(text=messages[self.game.result])
            self.disable_board()
        elif self.game.is_in_check():
            self.info_label.config(text=f"⚠️ Échec au roi {self.game.turn} !")
        else:
            self.info_label.config(text="")

        if self.game.game_over:
            self.claim_50_button.config(state=DISABLED)
            self.claim_3fold_button.config(state=DISABLED)
        else:
            self.claim_50_button.config(
                state=NORMAL if self.game.can_claim_fifty_move_draw() else DISABLED
            )
            self.claim_3fold_button.config(
                state=NORMAL if self.game.can_claim_threefold_repetition() else DISABLED
            )

    def disable_board(self):
        for row in range(8):
            for col in range(8):
                self.buttons[row][col].config(state=DISABLED)

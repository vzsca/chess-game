# ♟️ Chess Game

A simple two-player chess game written in Python with a Tkinter graphical interface.

The project is organized so that the chess rules are independent from the graphical interface.

## ✨ Features

- Two-player local chess
- Legal move validation with king-safety checks
- Check, checkmate and stalemate detection
- Castling with complete rook/king rights validation
- En passant
- Promotion to queen, rook, bishop or knight through a Tkinter popup
- FIDE draw rules: dead positions, threefold/fivefold repetition and 50/75-move rules
- Automatic terminal draws for fivefold repetition and 75 moves
- Claim buttons for the threefold repetition and 50-move rules
- Tkinter graphical interface
- Backend/frontend separation
- Automated backend tests
- No external Python dependencies

## 📁 Project structure

```text
chess-game/
├── backend/
│   ├── __init__.py
│   ├── board.py       # Board representation and helpers
│   ├── constants.py   # Pieces, colors and movement constants
│   ├── game.py        # Game state, moves and draw claims
│   └── moves.py       # Move generation, attacks and rule detection
├── frontend/
│   ├── __init__.py
│   └── ui.py          # Tkinter interface
├── tests/
│   └── test_chess.py  # Backend rule tests
├── .github/
│   └── workflows/
│       └── tests.yml  # Continuous integration
├── main.py            # Application entry point
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Run the game

Python 3.10+ is recommended.

```bash
python main.py
```

On Windows, if `python` is not recognized:

```bash
py main.py
```

Tkinter is included with most standard Python installations. On some Linux distributions it must be installed separately through the system package manager.

## 🧱 Architecture

The project keeps the original gameplay model intact: an 8×8 grid of Tkinter buttons, colored squares, Unicode chess pieces and click-based legal-move selection.

The responsibilities are separated as follows:

- **Backend**: board state, move generation, attack detection, special moves and FIDE draw rules. It does not depend on Tkinter.
- **Frontend**: displays the board, handles clicks and shows promotion/draw controls.
- **Entry point**: starts the application.

The backend may use a different internal organization without changing the visible board design or the core interaction model.

## 🧪 Tests

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

The same test command runs automatically in GitHub Actions on pushes and pull requests.

## 📜 Chess rules

The implementation follows the FIDE Laws of Chess for the rules relevant to this local board game, including check/checkmate, castling, en passant, promotion, dead positions, threefold/fivefold repetition and the 50/75-move rules.

Threefold repetition and the 50-move rule are claims; fivefold repetition and the 75-move rule are automatic draws. Checkmate takes precedence over the automatic 75-move draw, as required by the FIDE rules.

## 📜 License

This project is distributed under the MIT License. See `LICENSE`.

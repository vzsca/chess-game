# ♟️ Chess Game

A two-player chess game written in Python with a Tkinter graphical interface.

The project separates the chess engine from the graphical interface, with the backend responsible for validating moves and enforcing the rules of chess.

## ✨ Features

- Two-player local chess
- 8×8 Tkinter board with colored squares and Unicode pieces
- Legal move generation with king-safety validation
- Check, checkmate and stalemate detection
- Castling with king/rook movement rights and attacked-square validation
- En passant with legality checks, including pinned en-passant captures
- Promotion to **queen, rook, bishop or knight** through a Tkinter popup
- FIDE draw rules:
  - dead positions
  - threefold repetition (claimable)
  - fivefold repetition (automatic)
  - 50-move rule (claimable)
  - 75-move rule (automatic)
- Correct repetition identity, including castling rights and legally available en passant
- Automatic terminal-state detection
- Draw-claim buttons in the interface
- Backend/frontend separation
- Hardened public backend methods against invalid coordinates and values
- Protection against inconsistent or corrupted board/game states
- Extensive automated tests covering normal moves, special moves, terminal states, draw rules and invalid states
- GitHub Actions test workflow
- No external Python dependencies

## 📁 Project structure

```text
chess-game/
├── backend/
│   ├── __init__.py
│   ├── board.py       # Board representation and helpers
│   ├── constants.py   # Pieces, colors and movement constants
│   ├── game.py        # Game state, validation, moves and draw claims
│   └── moves.py       # Move generation, attacks and rule detection
├── frontend/
│   ├── __init__.py
│   └── ui.py          # Tkinter interface
├── tests/
│   └── test_chess.py  # Backend rule and edge-case tests
├── .github/
│   └── workflows/
│       └── tests.yml  # Continuous integration
├── main.py            # Application entry point
├── .gitignore
├── LICENSE
└── README.md
```

## 🚀 Run the game

Python **3.10+** is recommended.

```bash
python main.py
```

On Windows, if `python` is not recognized:

```bash
py main.py
```

Tkinter is included with most standard Python installations. On some Linux distributions it must be installed separately through the system package manager.

## 🧱 Architecture

The original gameplay model is preserved: an 8×8 grid of Tkinter buttons, colored squares, Unicode chess pieces and click-based legal-move selection.

### Backend

The backend is independent from Tkinter and handles:

- board representation and state
- legal move generation
- attack and check detection
- king safety
- castling
- en passant
- promotion
- checkmate and stalemate
- FIDE draw rules
- repetition tracking
- validation of externally modified game states

Public game operations validate coordinates, values and the internal state before modifying the game. Invalid or inconsistent states are rejected instead of being allowed to produce undefined behavior.

### Frontend

The frontend provides the original simple interaction model:

- click a piece to select it
- legal destinations are highlighted
- click a destination to move
- promotion opens a selection popup
- draw claims can be requested from the interface

The board design remains intentionally simple and lightweight.

## 🧪 Tests

Run the complete test suite with:

```bash
python -m unittest discover -s tests -v
```

The tests cover, among other cases:

- normal piece movement
- invalid coordinates and move inputs
- king safety
- capturing restrictions
- castling and castling-right loss
- en passant and en-passant pins
- all four promotion choices
- invalid promotion values
- checkmate and stalemate
- threefold/fivefold repetition
- 50/75-move rules
- dead positions
- repetition identity with effective en passant
- malformed board and game states
- attempts to move after the game has ended

The same test command is configured to run automatically in GitHub Actions on pushes and pull requests.

## 🔒 Security and robustness

This is a local desktop application and does not expose a network server or API.

The backend has been hardened against malformed direct inputs and inconsistent state, including:

- invalid or out-of-range coordinates
- invalid piece values
- malformed board dimensions
- missing or duplicated kings
- pawns placed on promotion ranks
- adjacent kings
- impossible pawn counts
- malformed castling rights
- invalid en-passant state
- invalid halfmove counters
- empty or invalid position history

These checks are intended to keep direct backend usage predictable and prevent corrupted game state from silently affecting move validation.

## 📜 Chess rules

The implementation follows the relevant **FIDE Laws of Chess** for this local board game, including check/checkmate, castling, en passant, promotion, dead positions, threefold/fivefold repetition and the 50/75-move rules.

Threefold repetition and the 50-move rule are **claimable** draws. Fivefold repetition and the 75-move rule are **automatic** draws. Checkmate takes precedence over the automatic 75-move draw.

The implementation intentionally focuses on the rules required for the board game itself; tournament procedures such as arbiter intervention, clocks, touch-move and notation are outside the current scope.

## 📜 License

This project is distributed under the MIT License. See `LICENSE`.

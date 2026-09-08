# ♟️ Chess Game

A simple two-player chess game written in Python with a Tkinter graphical interface.

The project is organized so that the chess rules are independent from the graphical interface.

## ✨ Features

- Two-player local chess
- Legal move validation
- Check, checkmate and stalemate detection
- Castling with rook validation
- Automatic queen promotion
- Tkinter graphical interface
- Backend/frontend separation
- No external Python dependencies

## 📁 Project structure

```text
chess-game/
├── backend/
│   ├── __init__.py
│   ├── board.py       # Board representation and helpers
│   ├── constants.py   # Pieces, colors and movement constants
│   └── moves.py       # Move generation and check detection
├── frontend/
│   ├── __init__.py
│   └── ui.py          # Tkinter interface
├── tests/
│   └── ...            # Automated tests
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

The project follows a simple separation of responsibilities:

- **Backend**: contains the board, chess rules and move validation. It does not depend on Tkinter.
- **Frontend**: displays the game and handles user interaction.
- **Entry point**: starts the application.

This makes the chess engine easier to test and allows another interface to be added later without rewriting the rules.

## 🛠️ Development

Clone the repository:

```bash
git clone https://github.com/vzsca/chess-game.git
cd chess-game
```

Optional virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\\Scripts\\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

## 🧪 Tests

Run the test suite with:

```bash
python -m unittest discover -s tests -v
```

## 📜 License

This project is distributed under the MIT License. See `LICENSE`.

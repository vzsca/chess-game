"""Application entry point."""
from tkinter import Tk
from frontend.ui import ChessUI


def main():
    root = Tk()
    root.title("Chess Game")
    ChessUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

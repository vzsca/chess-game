"""Chess move generation, attack detection and FIDE draw rules."""

from .board import copy_board, find_king, in_bounds, piece_color, same_color
from .constants import (
    EMPTY,
    ROOK_DIRECTIONS,
    BISHOP_DIRECTIONS,
    QUEEN_DIRECTIONS,
    KNIGHT_OFFSETS,
    KING_OFFSETS,
)

WHITE_KING = "♔"
BLACK_KING = "♚"
KINGS = WHITE_KING + BLACK_KING
PAWNS = "♙♟"
ROOKS = "♖♜"
BISHOPS = "♗♝"
KNIGHTS = "♘♞"
QUEENS = "♕♛"


def _is_king(piece):
    return piece in KINGS


def _is_capturable_target(piece):
    """Opponent pieces can be captured, but a king can never be captured."""
    return piece != EMPTY and not _is_king(piece)


def sliding_moves(board, row, col, directions):
    """Return normal sliding moves, stopping at the first occupied square."""
    result = []
    source = board[row][col]
    for dr, dc in directions:
        for step in range(1, 8):
            r, c = row + dr * step, col + dc * step
            if not in_bounds(r, c):
                break
            target = board[r][c]
            if target == EMPTY:
                result.append((r, c))
                continue
            if not same_color(source, target) and _is_capturable_target(target):
                result.append((r, c))
            break
    return result


def pseudo_moves(board, row, col):
    """Return attacked squares without checking whether the attacker exposes its king."""
    piece = board[row][col]
    if piece == EMPTY:
        return []
    if piece == "♙":
        return [(row - 1, c) for c in (col - 1, col + 1) if in_bounds(row - 1, c)]
    if piece == "♟":
        return [(row + 1, c) for c in (col - 1, col + 1) if in_bounds(row + 1, c)]
    if piece in KNIGHTS:
        return [
            (row + dr, col + dc)
            for dr, dc in KNIGHT_OFFSETS
            if in_bounds(row + dr, col + dc)
        ]
    if piece in KINGS:
        return [
            (row + dr, col + dc)
            for dr, dc in KING_OFFSETS
            if in_bounds(row + dr, col + dc)
        ]
    if piece in ROOKS:
        return sliding_moves(board, row, col, ROOK_DIRECTIONS)
    if piece in BISHOPS:
        return sliding_moves(board, row, col, BISHOP_DIRECTIONS)
    if piece in QUEENS:
        return sliding_moves(board, row, col, QUEEN_DIRECTIONS)
    return []


def is_square_attacked(board, row, col, by_color):
    """Return whether a square is attacked by the given side."""
    return any(
        piece_color(board[r][c]) == by_color
        and (row, col) in pseudo_moves(board, r, c)
        for r in range(8)
        for c in range(8)
    )


def is_in_check(board, color):
    """Return whether the given king is currently attacked."""
    king = find_king(board, color)
    if king is None:
        return True
    enemy = "noir" if color == "blanc" else "blanc"
    return is_square_attacked(board, king[0], king[1], enemy)


def _normal_moves(board, row, col):
    """Return pseudo-legal moves excluding castling and en passant."""
    piece = board[row][col]
    moves = []

    if piece == "♙":
        if in_bounds(row - 1, col) and board[row - 1][col] == EMPTY:
            moves.append((row - 1, col))
            if row == 6 and board[row - 2][col] == EMPTY:
                moves.append((row - 2, col))
        for dc in (-1, 1):
            r, c = row - 1, col + dc
            if (
                in_bounds(r, c)
                and not same_color(piece, board[r][c])
                and _is_capturable_target(board[r][c])
            ):
                moves.append((r, c))

    elif piece == "♟":
        if in_bounds(row + 1, col) and board[row + 1][col] == EMPTY:
            moves.append((row + 1, col))
            if row == 1 and board[row + 2][col] == EMPTY:
                moves.append((row + 2, col))
        for dc in (-1, 1):
            r, c = row + 1, col + dc
            if (
                in_bounds(r, c)
                and not same_color(piece, board[r][c])
                and _is_capturable_target(board[r][c])
            ):
                moves.append((r, c))

    elif piece in KNIGHTS:
        moves = [
            (row + dr, col + dc)
            for dr, dc in KNIGHT_OFFSETS
            if in_bounds(row + dr, col + dc)
            and (board[row + dr][col + dc] == EMPTY
                 or (not same_color(piece, board[row + dr][col + dc])
                     and _is_capturable_target(board[row + dr][col + dc])))
        ]

    elif piece in KINGS:
        moves = [
            (row + dr, col + dc)
            for dr, dc in KING_OFFSETS
            if in_bounds(row + dr, col + dc)
            and (board[row + dr][col + dc] == EMPTY
                 or (not same_color(piece, board[row + dr][col + dc])
                     and _is_capturable_target(board[row + dr][col + dc])))
        ]

    elif piece in ROOKS:
        moves = sliding_moves(board, row, col, ROOK_DIRECTIONS)
    elif piece in BISHOPS:
        moves = sliding_moves(board, row, col, BISHOP_DIRECTIONS)
    elif piece in QUEENS:
        moves = sliding_moves(board, row, col, QUEEN_DIRECTIONS)

    return moves


def _castling_moves(board, row, col, castling):
    """Return legal castling destinations, including all FIDE restrictions."""
    piece = board[row][col]
    color = piece_color(piece)
    if piece not in KINGS or castling[color]["king_moved"]:
        return []

    home = 7 if color == "blanc" else 0
    enemy = "noir" if color == "blanc" else "blanc"
    rook = "♖" if color == "blanc" else "♜"
    if (row, col) != (home, 4) or is_square_attacked(board, home, 4, enemy):
        return []

    result = []
    for side, rook_col, transit, destination in (
        ("king", 7, 5, 6),
        ("queen", 0, 3, 2),
    ):
        if castling[color][side + "_rook_moved"] or board[home][rook_col] != rook:
            continue

        between = range(5, 7) if side == "king" else range(1, 4)
        if any(board[home][c] != EMPTY for c in between):
            continue
        if any(is_square_attacked(board, home, c, enemy) for c in (transit, destination)):
            continue
        result.append((home, destination))

    return result


def legal_moves(board, row, col, castling, en_passant=None):
    """Return all legal destinations for one piece."""
    piece = board[row][col]
    if piece == EMPTY:
        return []

    candidates = _normal_moves(board, row, col)
    if piece in KINGS:
        candidates += _castling_moves(board, row, col, castling)

    if piece in PAWNS and en_passant is not None:
        direction = -1 if piece == "♙" else 1
        if en_passant[0] == row + direction and abs(en_passant[1] - col) == 1:
            adjacent = board[row][en_passant[1]]
            enemy_pawn = "♟" if piece == "♙" else "♙"
            if adjacent == enemy_pawn and board[en_passant[0]][en_passant[1]] == EMPTY:
                candidates.append(en_passant)

    color = piece_color(piece)
    legal = []
    for target_row, target_col in candidates:
        test = copy_board(board)
        test[target_row][target_col] = piece
        test[row][col] = EMPTY

        if piece in PAWNS and (target_row, target_col) == en_passant and board[target_row][target_col] == EMPTY:
            captured_row = target_row + (1 if piece == "♙" else -1)
            test[captured_row][target_col] = EMPTY

        # A king may move only to a square that is not attacked after the move.
        if not is_in_check(test, color):
            legal.append((target_row, target_col))

    return legal


def has_legal_move(board, color, castling, en_passant=None):
    return any(
        legal_moves(board, r, c, castling, en_passant)
        for r in range(8)
        for c in range(8)
        if piece_color(board[r][c]) == color
    )


def _dead_position_by_material(board):
    """Detect common FIDE dead positions that are provably unable to mate."""
    pieces = [p for row in board for p in row if p != EMPTY and p not in KINGS]
    if not pieces:
        return True

    # Any pawn, rook or queen leaves possible mating sequences.
    if any(piece in PAWNS + ROOKS + QUEENS for piece in pieces):
        return False

    # A lone bishop or knight against a king cannot mate.
    if len(pieces) == 1 and pieces[0] in BISHOPS + KNIGHTS:
        return True

    # King + bishop versus king + bishop is dead when both bishops live on
    # squares of the same colour: neither side can ever control the other
    # bishop's colour complex.
    if len(pieces) == 2 and all(piece in BISHOPS for piece in pieces):
        bishop_squares = []
        for r in range(8):
            for c in range(8):
                if board[r][c] in BISHOPS:
                    bishop_squares.append((r + c) % 2)
        return len(bishop_squares) == 2 and bishop_squares[0] == bishop_squares[1]

    return False


def game_state(board, color, castling, en_passant=None, halfmove_clock=0, history=None):
    """Return the terminal FIDE state, or None while the game continues.

    Automatic draws are fivefold repetition and 75 moves without a pawn move
    or capture. Threefold repetition and the 50-move rule are claims and are
    therefore exposed by ChessGame rather than ending the game automatically.
    """
    if not has_legal_move(board, color, castling, en_passant):
        return "mat" if is_in_check(board, color) else "pat"

    if _dead_position_by_material(board):
        return "nulle_materiel"

    if history is not None:
        current = history[-1]
        occurrences = sum(position == current for position in history)
        if occurrences >= 5:
            return "nulle_repetition_cinq"

    # FIDE Article 9.6.2: 75 moves by each player = 150 half-moves.
    if halfmove_clock >= 150:
        return "nulle_75_coups"

    return None

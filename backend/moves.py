"""Chess move generation and rule detection."""

from .board import copy_board, find_king, in_bounds, piece_color, same_color
from .constants import EMPTY, ROOK_DIRECTIONS, BISHOP_DIRECTIONS, QUEEN_DIRECTIONS, KNIGHT_OFFSETS, KING_OFFSETS


def sliding_moves(board, row, col, directions):
    result = []
    for dr, dc in directions:
        for step in range(1, 8):
            r, c = row + dr * step, col + dc * step
            if not in_bounds(r, c):
                break
            if board[r][c] == EMPTY:
                result.append((r, c))
                continue
            if not same_color(board[row][col], board[r][c]):
                result.append((r, c))
            break
    return result


def pseudo_moves(board, row, col):
    """Return squares attacked by a piece, without king-safety validation."""
    p = board[row][col]
    if p == EMPTY:
        return []
    if p == "♙":
        return [(row - 1, c) for c in (col - 1, col + 1) if in_bounds(row - 1, c)]
    if p == "♟":
        return [(row + 1, c) for c in (col - 1, col + 1) if in_bounds(row + 1, c)]
    if p in "♘♞":
        return [(row + dr, col + dc) for dr, dc in KNIGHT_OFFSETS if in_bounds(row + dr, col + dc)]
    if p in "♔♚":
        return [(row + dr, col + dc) for dr, dc in KING_OFFSETS if in_bounds(row + dr, col + dc)]
    if p in "♖♜":
        return sliding_moves(board, row, col, ROOK_DIRECTIONS)
    if p in "♗♝":
        return sliding_moves(board, row, col, BISHOP_DIRECTIONS)
    if p in "♕♛":
        return sliding_moves(board, row, col, QUEEN_DIRECTIONS)
    return []


def is_square_attacked(board, row, col, by_color):
    return any(
        piece_color(board[r][c]) == by_color and (row, col) in pseudo_moves(board, r, c)
        for r in range(8) for c in range(8)
    )


def is_in_check(board, color):
    king = find_king(board, color)
    if king is None:
        return True
    enemy = "noir" if color == "blanc" else "blanc"
    return is_square_attacked(board, king[0], king[1], enemy)


def _normal_moves(board, row, col):
    p = board[row][col]
    moves = []
    if p == "♙":
        if in_bounds(row - 1, col) and board[row - 1][col] == EMPTY:
            moves.append((row - 1, col))
            if row == 6 and board[row - 2][col] == EMPTY:
                moves.append((row - 2, col))
        for dc in (-1, 1):
            r, c = row - 1, col + dc
            if in_bounds(r, c) and board[r][c] != EMPTY and not same_color(p, board[r][c]):
                moves.append((r, c))
    elif p == "♟":
        if in_bounds(row + 1, col) and board[row + 1][col] == EMPTY:
            moves.append((row + 1, col))
            if row == 1 and board[row + 2][col] == EMPTY:
                moves.append((row + 2, col))
        for dc in (-1, 1):
            r, c = row + 1, col + dc
            if in_bounds(r, c) and board[r][c] != EMPTY and not same_color(p, board[r][c]):
                moves.append((r, c))
    elif p in "♘♞":
        moves = [(row + dr, col + dc) for dr, dc in KNIGHT_OFFSETS
                 if in_bounds(row + dr, col + dc) and not same_color(p, board[row + dr][col + dc])]
    elif p in "♔♚":
        moves = [(row + dr, col + dc) for dr, dc in KING_OFFSETS
                 if in_bounds(row + dr, col + dc) and not same_color(p, board[row + dr][col + dc])]
    elif p in "♖♜":
        moves = sliding_moves(board, row, col, ROOK_DIRECTIONS)
    elif p in "♗♝":
        moves = sliding_moves(board, row, col, BISHOP_DIRECTIONS)
    elif p in "♕♛":
        moves = sliding_moves(board, row, col, QUEEN_DIRECTIONS)
    return moves


def _castling_moves(board, row, col, castling):
    piece = board[row][col]
    color = piece_color(piece)
    if piece not in "♔♚" or castling[color]["king_moved"]:
        return []
    home = 7 if color == "blanc" else 0
    enemy = "noir" if color == "blanc" else "blanc"
    rook = "♖" if color == "blanc" else "♜"
    if (row, col) != (home, 4) or is_square_attacked(board, home, 4, enemy):
        return []

    result = []
    for side, rook_col, transit, destination in (
        ("king", 7, 5, 6), ("queen", 0, 3, 2)
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
    """Return all legal destinations, including en passant and castling."""
    p = board[row][col]
    if p == EMPTY:
        return []
    candidates = _normal_moves(board, row, col)
    if p in "♔♚":
        candidates += _castling_moves(board, row, col, castling)

    # En passant is legal only immediately after the opponent's double pawn move.
    if p in "♙♟" and en_passant is not None:
        direction = -1 if p == "♙" else 1
        if en_passant[0] == row + direction and abs(en_passant[1] - col) == 1:
            adjacent = board[row][en_passant[1]]
            enemy_pawn = "♟" if p == "♙" else "♙"
            if adjacent == enemy_pawn:
                candidates.append(en_passant)

    color = piece_color(p)
    legal = []
    for tr, tc in candidates:
        test = copy_board(board)
        test[tr][tc] = p
        test[row][col] = EMPTY
        if p in "♙♟" and (tr, tc) == en_passant and board[tr][tc] == EMPTY:
            captured_row = tr + (1 if p == "♙" else -1)
            test[captured_row][tc] = EMPTY
        if not is_in_check(test, color):
            legal.append((tr, tc))
    return legal


def has_legal_move(board, color, castling, en_passant=None):
    return any(
        legal_moves(board, r, c, castling, en_passant)
        for r in range(8) for c in range(8)
        if piece_color(board[r][c]) == color
    )


def _insufficient_material(board):
    """Detect the basic dead positions that cannot produce checkmate."""
    pieces = [p for row in board for p in row if p != EMPTY and p not in "♔♚"]
    if not pieces:
        return True
    if any(p in "♙♟♖♜♕♛" for p in pieces):
        return False
    # King + bishop(s) or king + knight(s) only. Two bishops can mate, so
    # only a single minor piece total is considered insufficient here.
    return len(pieces) == 1


def game_state(board, color, castling, en_passant=None, halfmove_clock=0, history=None):
    """Return None, mat, pat, or a draw reason."""
    if not has_legal_move(board, color, castling, en_passant):
        return "mat" if is_in_check(board, color) else "pat"
    if halfmove_clock >= 100:
        return "nulle_50_coups"
    if history is not None:
        current = history[-1]
        if sum(position == current for position in history) >= 3:
            return "nulle_repetition"
    if _insufficient_material(board):
        return "nulle_materiel"
    return None

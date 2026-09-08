"""Chess move generation and check detection."""
from .board import copy_board, find_king, in_bounds, piece_color, same_color
from .constants import EMPTY, ROOK_DIRECTIONS, BISHOP_DIRECTIONS, QUEEN_DIRECTIONS, KNIGHT_OFFSETS, KING_OFFSETS

def sliding_moves(board, row, col, directions):
    result = []
    for dr, dc in directions:
        for step in range(1, 8):
            r, c = row + dr * step, col + dc * step
            if not in_bounds(r, c): break
            if board[r][c] == EMPTY: result.append((r, c)); continue
            if not same_color(board[row][col], board[r][c]): result.append((r, c))
            break
    return result

def pseudo_moves(board, row, col):
    p = board[row][col]
    if p == EMPTY: return []
    if p == "♙": return [(row - 1, row_col) for row_col in (col - 1, col + 1) if in_bounds(row - 1, row_col)]
    if p == "♟": return [(row + 1, row_col) for row_col in (col - 1, col + 1) if in_bounds(row + 1, row_col)]
    if p in "♘♞": return [(row + dr, col + dc) for dr, dc in KNIGHT_OFFSETS if in_bounds(row + dr, col + dc)]
    if p in "♔♚": return [(row + dr, col + dc) for dr, dc in KING_OFFSETS if in_bounds(row + dr, col + dc)]
    if p in "♖♜": return sliding_moves(board, row, col, ROOK_DIRECTIONS)
    if p in "♗♝": return sliding_moves(board, row, col, BISHOP_DIRECTIONS)
    if p in "♕♛": return sliding_moves(board, row, col, QUEEN_DIRECTIONS)
    return []

def is_square_attacked(board, row, col, by_color):
    return any(piece_color(board[r][c]) == by_color and (row, col) in pseudo_moves(board, r, c)
               for r in range(8) for c in range(8))

def is_in_check(board, color):
    king = find_king(board, color)
    if king is None: return True
    enemy = "noir" if color == "blanc" else "blanc"
    return is_square_attacked(board, *king, enemy)

def _normal_moves(board, row, col):
    p = board[row][col]; moves = []
    if p == "♙":
        if in_bounds(row-1,col) and board[row-1][col] == EMPTY:
            moves.append((row-1,col))
            if row == 6 and board[row-2][col] == EMPTY: moves.append((row-2,col))
        for dc in (-1,1):
            r,c=row-1,col+dc
            if in_bounds(r,c) and board[r][c] != EMPTY and not same_color(p,board[r][c]): moves.append((r,c))
    elif p == "♟":
        if in_bounds(row+1,col) and board[row+1][col] == EMPTY:
            moves.append((row+1,col))
            if row == 1 and board[row+2][col] == EMPTY: moves.append((row+2,col))
        for dc in (-1,1):
            r,c=row+1,col+dc
            if in_bounds(r,c) and board[r][c] != EMPTY and not same_color(p,board[r][c]): moves.append((r,c))
    elif p in "♘♞": moves = [(row+dr,col+dc) for dr,dc in KNIGHT_OFFSETS if in_bounds(row+dr,col+dc) and not same_color(p,board[row+dr][col+dc])]
    elif p in "♔♚": moves = [(row+dr,col+dc) for dr,dc in KING_OFFSETS if in_bounds(row+dr,col+dc) and not same_color(p,board[row+dr][col+dc])]
    elif p in "♖♜": moves = sliding_moves(board,row,col,ROOK_DIRECTIONS)
    elif p in "♗♝": moves = sliding_moves(board,row,col,BISHOP_DIRECTIONS)
    elif p in "♕♛": moves = sliding_moves(board,row,col,QUEEN_DIRECTIONS)
    return moves

def legal_moves(board, row, col, castling):
    p = board[row][col]
    if p == EMPTY: return []
    color = piece_color(p); candidates = _normal_moves(board,row,col)
    if p in "♔♚" and not castling[color]["king_moved"]:
        home = 7 if color == "blanc" else 0; enemy = "noir" if color == "blanc" else "blanc"
        if (row,col) == (home,4) and not is_square_attacked(board,home,4,enemy):
            for side,rc,tc,dc in (("king",7,5,6),("queen",0,3,2)):
                rook = "♖" if color == "blanc" else "♜"
                if castling[color][side+"_rook_moved"] or board[home][rc] != rook: continue
                between = range(5,7) if side == "king" else range(1,4)
                if any(board[home][c] != EMPTY for c in between): continue
                if any(is_square_attacked(board,home,c,enemy) for c in (tc,dc)): continue
                candidates.append((home,dc))
    legal=[]
    for tr,tc in candidates:
        test=copy_board(board); test[tr][tc]=p; test[row][col]=EMPTY
        if not is_in_check(test,color): legal.append((tr,tc))
    return legal

def has_legal_move(board,color,castling):
    return any(legal_moves(board,r,c,castling) for r in range(8) for c in range(8) if piece_color(board[r][c]) == color)

def game_state(board,color,castling):
    if has_legal_move(board,color,castling): return None
    return "mat" if is_in_check(board,color) else "pat"

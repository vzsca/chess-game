from tkinter import *
import copy

BLANC = "♖♘♗♕♔♙"
NOIR = "♜♞♝♛♚♟"

# Suivi des mouvements pour la rocade
mouvements = {
    "♔": False, "♚": False,
    "♖a1": False, "♖h1": False,
    "♜a8": False, "♜h8": False
}

# ===============================
# === FONCTIONS DE LOGIQUE JEU ==
# ===============================

def init_plateau():
    """
    Initialise le plateau de jeu avec la disposition standard.

    Préconditions :
        - Aucune.
    Postconditions :
        - Retourne une liste 8x8 représentant l’échiquier initial.
    """
    return [
        ["♜","♞","♝","♛","♚","♝","♞","♜"],
        ["♟"]*8,
        [" "]*8,
        [" "]*8,
        [" "]*8,
        [" "]*8,
        ["♙"]*8,
        ["♖","♘","♗","♕","♔","♗","♘","♖"]
    ]

def dans_plateau(ligne, col):
    """
    Vérifie si la position (ligne, col) est dans les limites du plateau.

    Préconditions :
        - ligne et col sont des entiers compris entre 0 et 7.
    """
    return 0 <= ligne < 8 and 0 <= col < 8

def couleur_piece(piece):
    """
    Retourne la couleur d’une pièce ('blanc', 'noir') ou None si c’est une case vide.

    Préconditions :
        - piece est un caractère (chaîne de longueur 1).
    """
    if piece in BLANC: return "blanc"
    if piece in NOIR: return "noir"
    return None

def meme_couleur(p1, p2):
    """
    Vérifie si deux pièces sont de la même couleur.

    Préconditions :
        - p1 et p2 sont des caractères représentant des pièces ou des espaces.
    """
    return p1 != " " and p2 != " " and couleur_piece(p1) == couleur_piece(p2)

def copier_plateau(board):
    """
    Retourne une copie indépendante du plateau.

    Préconditions :
        - board est une liste de 8 sous-listes de longueur 8.
    """
    return [row.copy() for row in board]

def coups_glissants(board, ligne, col, directions):
    """
    Calcule les coups valides pour une pièce glissante (tour, fou, dame).

    Préconditions :
        - board est une liste 8x8 représentant le plateau.
        - ligne et col désignent une case valide.
        - directions est une liste de couples (dr, dc).
    """
    coups = []
    for dr, dc in directions:
        for i in range(1, 8):
            l, c = ligne + dr * i, col + dc * i
            if not dans_plateau(l, c): break
            cible = board[l][c]
            if cible == " ":
                coups.append((l, c))
            else:
                if not meme_couleur(board[ligne][col], cible):
                    coups.append((l, c))
                break
    return coups

def pseudo_coups(board, ligne, col):
    """
    Retourne tous les coups théoriques d'une pièce sans vérifier les échecs.

    Préconditions :
        - board est un plateau 8x8 valide.
        - ligne, col sont des entiers valides.
    """
    p = board[ligne][col]
    if p == " ": return []
    coups = []
    if p == "♙":
        for dc in (-1, 1):
            if dans_plateau(ligne - 1, col + dc):
                coups.append((ligne - 1, col + dc))
    elif p == "♟":
        for dc in (-1, 1):
            if dans_plateau(ligne + 1, col + dc):
                coups.append((ligne + 1, col + dc))
    elif p in "♘♞":
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            if dans_plateau(ligne + dr, col + dc):
                coups.append((ligne + dr, col + dc))
    elif p in "♔♚":
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if (dr != 0 or dc != 0) and dans_plateau(ligne + dr, col + dc):
                    coups.append((ligne + dr, col + dc))
    elif p in "♖♜":
        coups += coups_glissants(board, ligne, col, [(-1,0),(1,0),(0,-1),(0,1)])
    elif p in "♗♝":
        coups += coups_glissants(board, ligne, col, [(-1,-1),(-1,1),(1,-1),(1,1)])
    elif p in "♕♛":
        coups += coups_glissants(board, ligne, col,
                                 [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])
    return coups

def case_attaquee(board, ligne, col, couleur):
    """
    Indique si une case est attaquée par une couleur donnée.

    Préconditions :
        - board est un plateau valide.
        - ligne, col sont des entiers dans [0,7].
        - couleur ∈ {"blanc", "noir"}.
    """
    for l in range(8):
        for c in range(8):
            if couleur_piece(board[l][c]) == couleur:
                if (ligne, col) in pseudo_coups(board, l, c):
                    return True
    return False

def trouver_roi(board, couleur):
    """
    Renvoie la position du roi d’une couleur.

    Préconditions :
        - board est un plateau valide.
        - couleur ∈ {"blanc", "noir"}.
    """
    roi = "♔" if couleur == "blanc" else "♚"
    for l in range(8):
        for c in range(8):
            if board[l][c] == roi:
                return (l, c)
    return None

def en_echec(board, couleur):
    """
    Indique si le roi d’une couleur donnée est en échec.

    Préconditions :
        - board est un plateau 8x8 valide.
        - couleur ∈ {"blanc", "noir"}.
    """
    roi_pos = trouver_roi(board, couleur)
    if not roi_pos:
        return True
    return case_attaquee(board, roi_pos[0], roi_pos[1],
                         "noir" if couleur == "blanc" else "blanc")

def coups_legaux(board, ligne, col):
    """
    Calcule les coups légaux pour une pièce donnée (exclut les coups menant à un échec).

    Préconditions :
        - board est un plateau 8x8 valide.
        - ligne, col pointent une case contenant une pièce du joueur actif.
    """
    p = board[ligne][col]
    if p == " ": return []
    couleur = couleur_piece(p)
    coups = []

    # Logique spécifique selon la pièce (inchangée)
    if p == "♙":
        if dans_plateau(ligne-1, col) and board[ligne-1][col] == " ":
            coups.append((ligne-1, col))
            if ligne == 6 and board[ligne-2][col] == " ":
                coups.append((ligne-2, col))
        for dc in (-1, 1):
            l, c = ligne-1, col+dc
            if dans_plateau(l, c) and board[l][c] != " " and not meme_couleur(p, board[l][c]):
                coups.append((l, c))
    elif p == "♟":
        if dans_plateau(ligne+1, col) and board[ligne+1][col] == " ":
            coups.append((ligne+1, col))
            if ligne == 1 and board[ligne+2][col] == " ":
                coups.append((ligne+2, col))
        for dc in (-1, 1):
            l, c = ligne+1, col+dc
            if dans_plateau(l, c) and board[l][c] != " " and not meme_couleur(p, board[l][c]):
                coups.append((l, c))
    elif p in "♘♞":
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            l, c = ligne+dr, col+dc
            if dans_plateau(l, c) and not meme_couleur(p, board[l][c]):
                coups.append((l, c))
    elif p in "♔♚":
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr != 0 or dc != 0:
                    l, c = ligne+dr, col+dc
                    if dans_plateau(l, c) and not meme_couleur(p, board[l][c]):
                        coups.append((l, c))

        # Gestion des roques
        if p == "♔" and not mouvements["♔"]:
            if board[7][5]==" " and board[7][6]==" " and not case_attaquee(board,7,4,"noir") and not case_attaquee(board,7,5,"noir") and not case_attaquee(board,7,6,"noir"):
                coups.append((7,6))
            if board[7][1]==" " and board[7][2]==" " and board[7][3]==" " and not case_attaquee(board,7,2,"noir") and not case_attaquee(board,7,3,"noir") and not case_attaquee(board,7,4,"noir"):
                coups.append((7,2))
        elif p == "♚" and not mouvements["♚"]:
            if board[0][5]==" " and board[0][6]==" " and not case_attaquee(board,0,4,"blanc") and not case_attaquee(board,0,5,"blanc") and not case_attaquee(board,0,6,"blanc"):
                coups.append((0,6))
            if board[0][1]==" " and board[0][2]==" " and board[0][3]==" " and not case_attaquee(board,0,2,"blanc") and not case_attaquee(board,0,3,"blanc") and not case_attaquee(board,0,4,"blanc"):
                coups.append((0,2))
    elif p in "♖♜":
        coups += coups_glissants(board, ligne, col, [(-1,0),(1,0),(0,-1),(0,1)])
    elif p in "♗♝":
        coups += coups_glissants(board, ligne, col, [(-1,-1),(-1,1),(1,-1),(1,1)])
    elif p in "♕♛":
        coups += coups_glissants(board, ligne, col,
                                 [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)])

    legaux = []
    for l, c in coups:
        board2 = copier_plateau(board)
        board2[l][c] = p
        board2[ligne][col] = " "
        if not en_echec(board2, couleur):
            legaux.append((l, c))
    return legaux

def deplacer(board, de, vers):
    """
    Effectue un déplacement sur le plateau (y compris promotions et roques).

    Préconditions :
        - board est un plateau valide.
        - de et vers sont des tuples (ligne, col) valides.
    """
    l1, c1 = de
    l2, c2 = vers
    piece = board[l1][c1]
    board[l2][c2] = piece
    board[l1][c1] = " "

    # Promotion automatique
    if piece == "♙" and l2 == 0:
        board[l2][c2] = "♕"
    elif piece == "♟" and l2 == 7:
        board[l2][c2] = "♛"

    # Rocade
    if piece == "♔":
        mouvements["♔"] = True
        if de == (7,4) and vers == (7,6):
            board[7][5] = "♖"; board[7][7] = " "
        elif de == (7,4) and vers == (7,2):
            board[7][3] = "♖"; board[7][0] = " "
    elif piece == "♚":
        mouvements["♚"] = True
        if de == (0,4) and vers == (0,6):
            board[0][5] = "♜"; board[0][7] = " "
        elif de == (0,4) and vers == (0,2):
            board[0][3] = "♜"; board[0][0] = " "
    elif piece == "♖":
        if de == (7,0): mouvements["♖a1"] = True
        elif de == (7,7): mouvements["♖h1"] = True
    elif piece == "♜":
        if de == (0,0): mouvements["♜a8"] = True
        elif de == (0,7): mouvements["♜h8"] = True

    return board

def fin_partie(board, couleur):
    """
    Vérifie si la partie est terminée pour une couleur donnée.

    Préconditions :
        - board est un plateau valide.
        - couleur ∈ {"blanc", "noir"}.
    """
    coups = []
    for l in range(8):
        for c in range(8):
            if couleur_piece(board[l][c]) == couleur:
                coups += coups_legaux(board, l, c)
    if coups:
        return None
    return "mat" if en_echec(board, couleur) else "pat"

# ===============================
# === INTERFACE GRAPHIQUE =======
# ===============================

class EchecsUI:
    """
    Classe gérant l'interface graphique du jeu d'échecs avec Tkinter.
    """

    def __init__(self, root):
        """
        Initialise la fenêtre principale et le plateau graphique.

        Préconditions :
            - root est une instance de Tk().
        """
        self.root = root
        self.board = init_plateau()
        self.btns = [[None]*8 for _ in range(8)]
        self.turn = "blanc"
        self.sel = None
        self.moves = []

        self.label_tour = Label(root, text="Tour des blancs", font=("Arial", 14))
        self.label_tour.grid(row=8, column=0, columnspan=8)

        self.info = Label(root, text="", font=("Arial", 12))
        self.info.grid(row=9, column=0, columnspan=8)

        self.creer_ui()

    def creer_ui(self):
        """
        Crée l’ensemble des boutons représentant les cases du plateau.

        Préconditions :
            - self.board est une matrice 8x8.
        """
        for l in range(8):
            for c in range(8):
                couleur_bg = "white" if (l+c)%2==0 else "grey"
                b = Button(self.root, text=self.board[l][c], font=("Arial",17),
                           width=3, height=1, bg=couleur_bg,
                           command=lambda ll=l,cc=c: self.click(ll,cc))
                b.grid(row=l, column=c)
                self.btns[l][c] = b

    def rafraichir(self):
        """
        Met à jour le texte de chaque case après un déplacement.
        """
        for l in range(8):
            for c in range(8):
                self.btns[l][c].config(text=self.board[l][c])

    def clear_highlight(self):
        """
        Réinitialise les couleurs de fond des cases après sélection.
        """
        for l, c in self.moves:
            bg = "white" if (l+c)%2==0 else "grey"
            self.btns[l][c].config(bg=bg)
        if self.sel:
            l, c = self.sel
            bg = "white" if (l+c)%2==0 else "grey"
            self.btns[l][c].config(bg=bg)
        self.moves = []
        self.sel = None

    def highlight_moves(self, moves, piece):
        """
        Surligne les coups possibles d'une pièce sélectionnée.

        Préconditions :
            - moves est une liste de positions (l, c).
            - piece est un caractère représentant une pièce.
        """
        col = couleur_piece(piece)
        for l, c in moves:
            if self.board[l][c] == " ":
                self.btns[l][c].config(bg="green")
            elif couleur_piece(self.board[l][c]) != col:
                self.btns[l][c].config(bg="orange")
        self.moves = moves

    def click(self, l, c):
        """
        Gère le clic sur une case du plateau.

        Préconditions :
            - l, c sont des indices valides de la grille.
        """
        piece = self.board[l][c]

        if (l,c) in self.moves and self.sel:
            deplacer(self.board, self.sel, (l,c))
            self.clear_highlight()
            self.rafraichir()
            self.turn = "noir" if self.turn == "blanc" else "blanc"
            self.label_tour.config(text=f"Tour des {self.turn}s")
            adversaire = "noir" if self.turn == "blanc" else "blanc"
            self.info.config(text=f"⚠️ Échec au roi {self.turn} !" if en_echec(self.board,self.turn) else "")
            state = fin_partie(self.board, self.turn)
            if state == "mat":
                self.info.config(text=f"♛ Échec et mat ! Les {adversaire}s gagnent.")
                self.desactiver()
            elif state == "pat":
                self.info.config(text="🤝 Pat ! Match nul.")
                self.desactiver()
            return

        if couleur_piece(piece) == self.turn:
            self.clear_highlight()
            self.sel = (l, c)
            self.btns[l][c].config(bg="red")
            coups = coups_legaux(self.board, l, c)
            self.highlight_moves(coups, piece)
        else:
            self.clear_highlight()

    def desactiver(self):
        """
        Désactive toutes les cases à la fin de la partie.
        """
        for l in range(8):
            for c in range(8):
                self.btns[l][c].config(state=DISABLED)


def main():
    """
    Lance la fenêtre principale du jeu.

    Préconditions :
        - Aucune.
    """
    root = Tk()
    EchecsUI(root)
    root.mainloop()

main()

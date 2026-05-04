import tkinter as tk
from tkinter import messagebox, font
import copy
import math
import random
import threading
import time

# ── Constantes ──────────────────────────────────────────────────────────────
BOARD_SIZE = 8
SQ = 78          # taille d'une case en pixels
MARGIN = 36      # marge autour du plateau

# Couleurs
C_LIGHT   = "#F0D9B5"
C_DARK    = "#B58863"
C_SEL     = "#F6F669"
C_MOVE    = "#CDD26A"
C_LAST    = "#AAA23A"
C_CHECK   = "#E44032"
C_BG      = "#1A1A2E"
C_PANEL   = "#16213E"
C_TEXT    = "#E8E8E8"
C_ACCENT  = "#E2B04A"
C_COORD   = "#8B7355"

PIECES_UNICODE = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',
}

# Valeurs des pièces pour l'IA
PIECE_VALUES = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}

# Tables de positionnement (pour l'IA)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0,
]
KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]
BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]
ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0,
]
QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]
KING_TABLE_MID = [
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20,
]

TABLES = {'P': PAWN_TABLE, 'N': KNIGHT_TABLE, 'B': BISHOP_TABLE,
          'R': ROOK_TABLE, 'Q': QUEEN_TABLE, 'K': KING_TABLE_MID}


# ── Logique de jeu ───────────────────────────────────────────────────────────
def init_board():
    b = [[None]*8 for _ in range(8)]
    order = ['R','N','B','Q','K','B','N','R']
    for c, color in enumerate(['b','w']):
        row = 0 if color == 'b' else 7
        for col, p in enumerate(order):
            b[row][col] = color + p
        pawn_row = 1 if color == 'b' else 6
        for col in range(8):
            b[pawn_row][col] = color + 'P'
    return b

def pos(row, col): return row*8+col

def get_raw_moves(board, row, col, en_passant=None):
    """Tous les coups d'une pièce sans vérifier l'échec."""
    piece = board[row][col]
    if not piece: return []
    color, ptype = piece[0], piece[1]
    opp = 'b' if color == 'w' else 'w'
    moves = []

    def in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8
    def add(r, c):
        if in_bounds(r, c) and (not board[r][c] or board[r][c][0] == opp):
            moves.append((r, c))
            return board[r][c] is None
        return False
    def slide(dirs):
        for dr, dc in dirs:
            r, c = row+dr, col+dc
            while in_bounds(r, c):
                if board[r][c]:
                    if board[r][c][0] == opp: moves.append((r, c))
                    break
                moves.append((r, c))
                r += dr; c += dc

    if ptype == 'P':
        direction = -1 if color == 'w' else 1
        start_row = 6 if color == 'w' else 1
        r = row + direction
        if in_bounds(r, col) and not board[r][col]:
            moves.append((r, col))
            if row == start_row and not board[r+direction][col]:
                moves.append((r+direction, col))
        for dc in [-1, 1]:
            c = col + dc
            if in_bounds(r, c):
                if board[r][c] and board[r][c][0] == opp:
                    moves.append((r, c))
                elif en_passant == (r, c):
                    moves.append((r, c))

    elif ptype == 'N':
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            add(row+dr, col+dc)

    elif ptype == 'B': slide([(-1,-1),(-1,1),(1,-1),(1,1)])
    elif ptype == 'R': slide([(-1,0),(1,0),(0,-1),(0,1)])
    elif ptype == 'Q': slide([(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])
    elif ptype == 'K':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr or dc: add(row+dr, col+dc)

    return moves

def find_king(board, color):
    for r in range(8):
        for c in range(8):
            if board[r][c] == color+'K':
                return r, c
    return None

def is_attacked(board, row, col, by_color):
    """La case (row,col) est-elle attaquée par by_color ?"""
    opp = by_color
    # Simuler pièces adverses
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c][0] == opp:
                if (row, col) in get_raw_moves(board, r, c):
                    return True
    return False

def in_check(board, color):
    kr, kc = find_king(board, color)
    if kr is None: return False
    opp = 'b' if color == 'w' else 'w'
    return is_attacked(board, kr, kc, opp)

def apply_move(board, fr, fc, tr, tc, promotion='Q', en_passant=None, castling_rights=None):
    """Retourne un nouveau plateau après un coup (immuable)."""
    b = copy.deepcopy(board)
    piece = b[fr][fc]
    color, ptype = piece[0], piece[1]

    # En passant capture
    if ptype == 'P' and en_passant and (tr, tc) == en_passant:
        cap_row = fr  # la rangée du pion capturé
        b[cap_row][tc] = None

    b[tr][tc] = piece
    b[fr][fc] = None

    # Promotion
    if ptype == 'P' and (tr == 0 or tr == 7):
        b[tr][tc] = color + promotion

    # Roque
    if ptype == 'K':
        if tc - fc == 2:   # grand roque
            b[tr][5] = b[tr][7]; b[tr][7] = None
        elif fc - tc == 2: # petit roque
            b[tr][3] = b[tr][0]; b[tr][0] = None

    return b

def get_castling_moves(board, color, castling_rights):
    """Retourne les cases de destination du roi pour le roque."""
    moves = []
    row = 7 if color == 'w' else 0
    opp = 'b' if color == 'w' else 'w'
    kr, kc = find_king(board, color)
    if kr != row or kc != 4: return []
    if in_check(board, color): return []

    # Roque côté roi (kingside)
    ks_key = color + 'K'
    if castling_rights.get(ks_key, False):
        if not board[row][5] and not board[row][6]:
            if not is_attacked(board, row, 5, opp) and not is_attacked(board, row, 6, opp):
                moves.append((row, 6))

    # Roque côté dame (queenside)
    qs_key = color + 'Q'
    if castling_rights.get(qs_key, False):
        if not board[row][3] and not board[row][2] and not board[row][1]:
            if not is_attacked(board, row, 3, opp) and not is_attacked(board, row, 2, opp):
                moves.append((row, 2))

    return moves

def get_legal_moves(board, row, col, en_passant=None, castling_rights=None):
    """Tous les coups légaux d'une pièce (sans se mettre en échec)."""
    piece = board[row][col]
    if not piece: return []
    color, ptype = piece[0], piece[1]

    raw = get_raw_moves(board, row, col, en_passant)

    # Ajouter le roque
    if ptype == 'K' and castling_rights:
        raw += get_castling_moves(board, color, castling_rights)

    legal = []
    for tr, tc in raw:
        nb = apply_move(board, row, col, tr, tc, en_passant=en_passant)
        if not in_check(nb, color):
            legal.append((tr, tc))
    return legal

def all_legal_moves(board, color, en_passant=None, castling_rights=None):
    moves = []
    for r in range(8):
        for c in range(8):
            if board[r][c] and board[r][c][0] == color:
                for tr, tc in get_legal_moves(board, r, c, en_passant, castling_rights):
                    moves.append((r, c, tr, tc))
    return moves

def update_castling_rights(rights, piece, fr, fc):
    r = copy.copy(rights)
    if piece == 'wK': r['wK'] = r['wQ'] = False
    elif piece == 'bK': r['bK'] = r['bQ'] = False
    elif piece == 'wR':
        if fc == 7: r['wK'] = False
        elif fc == 0: r['wQ'] = False
    elif piece == 'bR':
        if fc == 7: r['bK'] = False
        elif fc == 0: r['bQ'] = False
    return r


# ── IA : Minimax + Alpha-Beta ─────────────────────────────────────────────────
def evaluate(board):
    score = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if not p: continue
            color, ptype = p[0], p[1]
            val = PIECE_VALUES[ptype]
            idx = pos(r, c) if color == 'b' else pos(7-r, c)
            table_bonus = TABLES[ptype][idx]
            if color == 'w':
                score += val + table_bonus
            else:
                score -= val + table_bonus
    return score

def minimax(board, depth, alpha, beta, maximizing, color, en_passant, castling_rights):
    opp = 'b' if color == 'w' else 'w'
    moves = all_legal_moves(board, color, en_passant, castling_rights)

    if depth == 0 or not moves:
        if not moves:
            if in_check(board, color):
                return -99999 if maximizing else 99999
            return 0  # pat
        return evaluate(board)

    if maximizing:
        best = -math.inf
        for fr, fc, tr, tc in moves:
            nb = apply_move(board, fr, fc, tr, tc, en_passant=en_passant)
            piece = board[fr][fc]
            # En passant suivant
            new_ep = None
            if piece[1] == 'P' and abs(tr - fr) == 2:
                new_ep = ((fr + tr)//2, fc)
            new_cr = update_castling_rights(castling_rights, piece, fr, fc)
            val = minimax(nb, depth-1, alpha, beta, False, opp, new_ep, new_cr)
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha: break
        return best
    else:
        best = math.inf
        for fr, fc, tr, tc in moves:
            nb = apply_move(board, fr, fc, tr, tc, en_passant=en_passant)
            piece = board[fr][fc]
            new_ep = None
            if piece[1] == 'P' and abs(tr - fr) == 2:
                new_ep = ((fr + tr)//2, fc)
            new_cr = update_castling_rights(castling_rights, piece, fr, fc)
            val = minimax(nb, depth-1, alpha, beta, True, opp, new_ep, new_cr)
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha: break
        return best

def best_ai_move(board, color, en_passant, castling_rights, depth=3):
    moves = all_legal_moves(board, color, en_passant, castling_rights)
    if not moves: return None
    random.shuffle(moves)
    opp = 'b' if color == 'w' else 'w'
    best_val = -math.inf if color == 'w' else math.inf
    best_move = moves[0]

    for fr, fc, tr, tc in moves:
        nb = apply_move(board, fr, fc, tr, tc, en_passant=en_passant)
        piece = board[fr][fc]
        new_ep = None
        if piece[1] == 'P' and abs(tr - fr) == 2:
            new_ep = ((fr + tr)//2, fc)
        new_cr = update_castling_rights(castling_rights, piece, fr, fc)
        val = minimax(nb, depth-1, -math.inf, math.inf, color == 'b', opp, new_ep, new_cr)
        if (color == 'w' and val > best_val) or (color == 'b' and val < best_val):
            best_val = val
            best_move = (fr, fc, tr, tc)

    return best_move


# ── Interface Tkinter ─────────────────────────────────────────────────────────
class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Échecs ♙")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        self.board = init_board()
        self.turn = 'w'
        self.selected = None
        self.legal_targets = []
        self.en_passant = None
        self.castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}
        self.last_move = None
        self.move_history = []
        self.game_over = False
        self.ai_color = 'b'
        self.ai_thinking = False
        self.ai_depth = 3

        self.setup_fonts()
        self.build_ui()
        self.draw_board()

    def setup_fonts(self):
        self.font_piece  = font.Font(family="Segoe UI Symbol", size=42)
        self.font_coord  = font.Font(family="Georgia", size=11, weight="bold")
        self.font_title  = font.Font(family="Georgia", size=20, weight="bold")
        self.font_status = font.Font(family="Georgia", size=12)
        self.font_move   = font.Font(family="Courier New", size=10)
        self.font_btn    = font.Font(family="Georgia", size=11, weight="bold")

    def build_ui(self):
        # Cadre principal
        main = tk.Frame(self.root, bg=C_BG)
        main.pack(padx=20, pady=20)

        # Titre
        tk.Label(main, text="♔  ÉCHECS  ♚", font=self.font_title,
                 bg=C_BG, fg=C_ACCENT).pack(pady=(0,12))

        content = tk.Frame(main, bg=C_BG)
        content.pack()

        # Canvas du plateau
        canvas_size = BOARD_SIZE * SQ + 2 * MARGIN
        self.canvas = tk.Canvas(content, width=canvas_size, height=canvas_size,
                                bg=C_BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=(0, 16))
        self.canvas.bind("<Button-1>", self.on_click)

        # Panneau latéral
        panel = tk.Frame(content, bg=C_PANEL, bd=0, relief='flat',
                         width=220)
        panel.pack(side=tk.LEFT, fill=tk.Y)
        panel.pack_propagate(False)

        # Statut
        tk.Label(panel, text="STATUT", font=font.Font(family="Georgia", size=9),
                 bg=C_PANEL, fg="#666").pack(pady=(16,2))
        self.status_var = tk.StringVar(value="Blancs jouent")
        self.status_lbl = tk.Label(panel, textvariable=self.status_var,
                                   font=self.font_status, bg=C_PANEL, fg=C_ACCENT,
                                   wraplength=200, justify='center')
        self.status_lbl.pack(pady=(0,12))

        # Séparateur
        tk.Frame(panel, height=1, bg="#2A3050").pack(fill=tk.X, padx=12)

        # Mode de jeu
        tk.Label(panel, text="MODE", font=font.Font(family="Georgia", size=9),
                 bg=C_PANEL, fg="#666").pack(pady=(12,4))

        self.mode_var = tk.StringVar(value="vsIA")
        modes_frame = tk.Frame(panel, bg=C_PANEL)
        modes_frame.pack()
        for text, val in [("vs IA", "vsIA"), ("2 joueurs", "vs2")]:
            tk.Radiobutton(modes_frame, text=text, variable=self.mode_var,
                           value=val, bg=C_PANEL, fg=C_TEXT,
                           selectcolor=C_PANEL, activebackground=C_PANEL,
                           font=self.font_btn, command=self.new_game).pack(side=tk.LEFT, padx=6)

        # Difficulté
        tk.Label(panel, text="DIFFICULTÉ", font=font.Font(family="Georgia", size=9),
                 bg=C_PANEL, fg="#666").pack(pady=(10,4))
        self.diff_var = tk.IntVar(value=3)
        diff_frame = tk.Frame(panel, bg=C_PANEL)
        diff_frame.pack()
        for label, depth in [("Facile", 1), ("Moyen", 3), ("Difficile", 4)]:
            tk.Radiobutton(diff_frame, text=label, variable=self.diff_var,
                           value=depth, bg=C_PANEL, fg=C_TEXT,
                           selectcolor=C_PANEL, activebackground=C_PANEL,
                           font=font.Font(family="Georgia", size=9),
                           command=lambda d=depth: setattr(self, 'ai_depth', d)).pack(side=tk.LEFT, padx=3)

        # Séparateur
        tk.Frame(panel, height=1, bg="#2A3050").pack(fill=tk.X, padx=12, pady=10)

        # Historique des coups
        tk.Label(panel, text="HISTORIQUE", font=font.Font(family="Georgia", size=9),
                 bg=C_PANEL, fg="#666").pack()

        hist_frame = tk.Frame(panel, bg=C_PANEL)
        hist_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        self.hist_text = tk.Text(hist_frame, width=22, height=14,
                                  bg="#0F1629", fg="#A0B0C0",
                                  font=self.font_move, bd=0,
                                  highlightthickness=1,
                                  highlightbackground="#2A3050",
                                  state='disabled', wrap='word')
        scrollbar = tk.Scrollbar(hist_frame, command=self.hist_text.yview)
        self.hist_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.hist_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bouton nouvelle partie
        tk.Button(panel, text="✦  Nouvelle Partie",
                  font=self.font_btn, bg="#2A3050", fg=C_ACCENT,
                  activebackground="#3A4060", activeforeground=C_ACCENT,
                  bd=0, pady=8, cursor="hand2",
                  command=self.new_game).pack(fill=tk.X, padx=12, pady=(6,16))

    def sq_to_xy(self, row, col):
        x = MARGIN + col * SQ
        y = MARGIN + row * SQ
        return x, y

    def xy_to_sq(self, x, y):
        col = (x - MARGIN) // SQ
        row = (y - MARGIN) // SQ
        if 0 <= row < 8 and 0 <= col < 8:
            return row, col
        return None, None

    def draw_board(self):
        self.canvas.delete("all")
        self.draw_squares()
        self.draw_highlights()
        self.draw_coordinates()
        self.draw_pieces()

    def draw_squares(self):
        for r in range(8):
            for c in range(8):
                x, y = self.sq_to_xy(r, c)
                color = C_LIGHT if (r + c) % 2 == 0 else C_DARK
                self.canvas.create_rectangle(x, y, x+SQ, y+SQ, fill=color, outline="")

    def draw_highlights(self):
        # Dernier coup
        if self.last_move:
            fr, fc, tr, tc = self.last_move
            for r, c in [(fr, fc), (tr, tc)]:
                x, y = self.sq_to_xy(r, c)
                base = C_LIGHT if (r+c)%2==0 else C_DARK
                self.canvas.create_rectangle(x, y, x+SQ, y+SQ,
                    fill=C_LAST, outline="")

        # Case sélectionnée
        if self.selected:
            r, c = self.selected
            x, y = self.sq_to_xy(r, c)
            self.canvas.create_rectangle(x, y, x+SQ, y+SQ, fill=C_SEL, outline="")

        # Coups légaux
        for r, c in self.legal_targets:
            x, y = self.sq_to_xy(r, c)
            cx, cy = x + SQ//2, y + SQ//2
            if self.board[r][c]:  # capture
                self.canvas.create_oval(x+2, y+2, x+SQ-2, y+SQ-2,
                    outline=C_MOVE, width=3, fill="")
            else:
                self.canvas.create_oval(cx-10, cy-10, cx+10, cy+10,
                    fill=C_MOVE, outline="")

        # Roi en échec
        if in_check(self.board, self.turn):
            kr, kc = find_king(self.board, self.turn)
            if kr is not None:
                x, y = self.sq_to_xy(kr, kc)
                self.canvas.create_rectangle(x, y, x+SQ, y+SQ, fill=C_CHECK, outline="")

    def draw_coordinates(self):
        files = "abcdefgh"
        for i in range(8):
            # Colonnes (bas)
            x = MARGIN + i*SQ + SQ//2
            y = MARGIN + 8*SQ + 6
            self.canvas.create_text(x, y, text=files[i],
                font=self.font_coord, fill=C_COORD)
            # Rangées (gauche)
            x2 = MARGIN - 14
            y2 = MARGIN + (7-i)*SQ + SQ//2
            self.canvas.create_text(x2, y2, text=str(i+1),
                font=self.font_coord, fill=C_COORD)

    def draw_pieces(self):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p:
                    x, y = self.sq_to_xy(r, c)
                    cx, cy = x + SQ//2, y + SQ//2
                    sym = PIECES_UNICODE[p]
                    # Ombre
                    self.canvas.create_text(cx+1, cy+2, text=sym,
                        font=self.font_piece, fill="#00000033")
                    # Pièce
                    color = "#FFFFF0" if p[0] == 'w' else "#1A1A2E"
                    self.canvas.create_text(cx, cy, text=sym,
                        font=self.font_piece, fill=color)

    def on_click(self, event):
        if self.game_over or self.ai_thinking: return
        if self.mode_var.get() == "vsIA" and self.turn == self.ai_color: return

        row, col = self.xy_to_sq(event.x, event.y)
        if row is None: return

        if self.selected:
            if (row, col) in self.legal_targets:
                self.do_move(self.selected[0], self.selected[1], row, col)
                return
            self.selected = None
            self.legal_targets = []

        p = self.board[row][col]
        if p and p[0] == self.turn:
            self.selected = (row, col)
            self.legal_targets = get_legal_moves(
                self.board, row, col, self.en_passant, self.castling_rights)

        self.draw_board()

    def do_move(self, fr, fc, tr, tc, promotion='Q'):
        piece = self.board[fr][fc]

        # Promotion : demander à l'utilisateur
        if piece[1] == 'P' and (tr == 0 or tr == 7):
            promotion = self.ask_promotion(piece[0])

        # Appliquer
        self.board = apply_move(self.board, fr, fc, tr, tc, promotion,
                                self.en_passant, self.castling_rights)
        self.castling_rights = update_castling_rights(self.castling_rights, piece, fr, fc)

        # En passant suivant
        self.en_passant = None
        if piece[1] == 'P' and abs(tr - fr) == 2:
            self.en_passant = ((fr + tr)//2, fc)

        self.last_move = (fr, fc, tr, tc)
        self.selected = None
        self.legal_targets = []

        # Historique
        self.log_move(piece, fr, fc, tr, tc, promotion)

        # Changer de tour
        self.turn = 'b' if self.turn == 'w' else 'w'
        self.check_game_state()
        self.draw_board()

        # Tour IA
        if not self.game_over and self.mode_var.get() == "vsIA" and self.turn == self.ai_color:
            self.root.after(200, self.ai_play)

    def ask_promotion(self, color):
        pieces = ['Q', 'R', 'B', 'N']
        names  = {'Q': 'Dame', 'R': 'Tour', 'B': 'Fou', 'N': 'Cavalier'}
        syms   = {p: PIECES_UNICODE[color+p] for p in pieces}
        result = [pieces[0]]

        dlg = tk.Toplevel(self.root)
        dlg.title("Promotion")
        dlg.configure(bg=C_PANEL)
        dlg.resizable(False, False)
        dlg.grab_set()
        tk.Label(dlg, text="Choisissez la promotion :", font=self.font_status,
                 bg=C_PANEL, fg=C_TEXT).pack(pady=(16,8), padx=20)
        for p in pieces:
            tk.Button(dlg, text=f"{syms[p]}  {names[p]}",
                      font=font.Font(family="Segoe UI Symbol", size=14),
                      bg="#2A3050", fg=C_ACCENT, activebackground="#3A4060",
                      activeforeground=C_ACCENT, bd=0, padx=16, pady=6,
                      command=lambda x=p: [result.__setitem__(0, x), dlg.destroy()]
                      ).pack(fill=tk.X, padx=20, pady=4)
        self.root.wait_window(dlg)
        return result[0]

    def check_game_state(self):
        moves = all_legal_moves(self.board, self.turn, self.en_passant, self.castling_rights)
        if not moves:
            self.game_over = True
            if in_check(self.board, self.turn):
                winner = "Noirs" if self.turn == 'w' else "Blancs"
                self.status_var.set(f"Échec et mat !\n{winner} gagnent 🏆")
            else:
                self.status_var.set("Pat ! Match nul 🤝")
        else:
            if in_check(self.board, self.turn):
                player = "Blancs" if self.turn == 'w' else "Noirs"
                self.status_var.set(f"⚠️ {player} en échec !")
            else:
                player = "Blancs" if self.turn == 'w' else "Noirs"
                suffix = " (IA pense…)" if self.mode_var.get() == "vsIA" and self.turn == self.ai_color else ""
                self.status_var.set(f"{player} jouent{suffix}")

    def ai_play(self):
        if self.game_over: return
        self.ai_thinking = True
        self.status_var.set("IA réfléchit… ♟")

        def run():
            depth = self.diff_var.get()
            move = best_ai_move(self.board, self.ai_color,
                                self.en_passant, self.castling_rights, depth)
            self.root.after(0, lambda: self.finish_ai(move))

        threading.Thread(target=run, daemon=True).start()

    def finish_ai(self, move):
        self.ai_thinking = False
        if move:
            fr, fc, tr, tc = move
            self.do_move(fr, fc, tr, tc)

    def log_move(self, piece, fr, fc, tr, tc, promotion):
        files = "abcdefgh"
        move_num = len(self.move_history) // 2 + 1
        mv = f"{files[fc]}{8-fr}→{files[tc]}{8-tr}"
        if piece[1] == 'P' and (tr == 0 or tr == 7):
            mv += f"={promotion}"
        if piece[0] == 'w':
            entry = f"{move_num:2d}. {mv:<10}"
        else:
            entry = f"    {mv}\n"
        self.move_history.append(entry)

        self.hist_text.configure(state='normal')
        self.hist_text.insert(tk.END, entry)
        self.hist_text.see(tk.END)
        self.hist_text.configure(state='disabled')

    def new_game(self):
        self.board = init_board()
        self.turn = 'w'
        self.selected = None
        self.legal_targets = []
        self.en_passant = None
        self.castling_rights = {'wK': True, 'wQ': True, 'bK': True, 'bQ': True}
        self.last_move = None
        self.move_history = []
        self.game_over = False
        self.ai_thinking = False
        self.ai_depth = self.diff_var.get()
        self.status_var.set("Blancs jouent")
        self.hist_text.configure(state='normal')
        self.hist_text.delete("1.0", tk.END)
        self.hist_text.configure(state='disabled')
        self.draw_board()


# ── Point d'entrée ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
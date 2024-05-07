import chess
import chess.engine
import random
from reconchess import *
from collections import Counter
class RandomSensingAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.possible_states = set()
        self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color
        self.possible_states = {board.fen()}

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if captured_my_piece:
            if capture_square is not None:
                self.possible_states = {fen for fen in self.possible_states if chess.Board(fen).piece_at(capture_square) is not None}
        else:
            if capture_square is not None:
                self.possible_states = {fen for fen in self.possible_states if chess.Board(fen).piece_at(capture_square) is None}

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        
        
        valid_center_squares = [square for square in sense_actions if square in center_squares]
        
        if valid_center_squares:
            return random.choice(valid_center_squares)
        else:
        
            return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.possible_states = compare_state_window(self.possible_states, sense_result)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        num_states = len(self.possible_states)
        if num_states > 10000:
            self.possible_states = set(random.sample(self.possible_states, 10000))
            num_states = 10000

        moves = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            if board.is_check():
                king_square = board.king(not board.turn)
                for move in board.legal_moves:
                    if move.to_square == king_square:
                        moves.append(move)
                        break
            else:
                result = self.engine.play(board, chess.engine.Limit(time=10/num_states, depth=10))
                moves.append(result.move)

        move_counts = Counter(moves)
        if move_counts:
            most_common_move = max(move_counts, key=move_counts.get)
            return most_common_move
        else:
            if move_actions:
                return random.choice(move_actions)
            else:
                return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
        captured_opponent_piece: bool, capture_square: Optional[Square]):
        if requested_move != taken_move:
            self.possible_states = [state for state in self.possible_states if state.is_legal(taken_move)]
        
        if captured_opponent_piece:
            self.possible_states = [state for state in self.possible_states if state.piece_at(capture_square) is None]

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        self.engine.quit()


def make_move(fen_string, move_string):
    board = chess.Board(fen_string)
    move = chess.Move.from_uci(move_string)

    board.push(move)
    return board.fen()

def generate_next_moves(fen_string):
    board = chess.Board(fen_string)
    moves = []
    
    for move in board.generate_pseudo_legal_moves():
        uci = move.uci()
        moves.append(uci)

    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        if not utilities.is_illegal_castle(board, move):
            uci = move.uci()
            if uci not in moves:
                moves.append(uci)

    return sorted(moves)

def generate_next_moves_capture(fen_string, capture_square):
    board = chess.Board(fen_string)
    target_square = chess.parse_square(capture_square)
    capture_moves = []
    
    for move in board.legal_moves:
        if move.to_square == target_square and board.is_capture(move):
            uci = move.uci() 
            capture_moves.append(uci)
    
    return sorted(capture_moves)

def generate_next_positions(fen_string, possible_moves):
    fen_possibilites = []
    for possible_move in possible_moves:
        fen_possibilites.append(make_move(fen_string, possible_move))

    return sorted(fen_possibilites)

def compare_state_window(fen_states, sense_result):
    fen_results = []
    for fen_string in fen_states:
        board = chess.Board(fen_string)
        
        match = True
        for square, piece in sense_result:
            board_square = chess.Square(square)
            board_piece = board.piece_at(board_square)
            
            if piece is None:
                if board_piece is not None:
                    match = False
                    break
            else:
                if board_piece is None or \
                    (board_piece.color == chess.WHITE and board_piece.symbol().upper() != piece.symbol().upper()) or \
                    (board_piece.color == chess.BLACK and board_piece.symbol().lower() != piece.symbol().lower()):
                    match = False
                    break
        
        if match:
            fen_results.append(fen_string)
    
    return sorted(fen_results)
import chess
import chess.engine
import random
from reconchess import *
from collections import Counter
import numpy as np

class ImprovedAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.possible_states = set()
        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish', setpgrp=True)
        self.opponent_moves = []
        self.sensing_heatmap = {square: 0 for square in chess.SQUARES}
        self.move_history = []
        self.sensing_history = []

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
        # Prioritize sensing squares that reduce the uncertainty of the game state
        uncertain_squares = self.get_uncertain_squares()
        if uncertain_squares:
            return self.select_sensing_square(uncertain_squares, move_actions, seconds_left)
        else:
            return self.sense_center_squares(sense_actions)

    def get_uncertain_squares(self) -> List[Square]:
        uncertain_squares = []
        for square in chess.SQUARES:
            piece_counts = Counter(board.piece_at(square) for board in [chess.Board(fen) for fen in self.possible_states])
            if len(piece_counts) > 1:
                uncertain_squares.append(square)
        return uncertain_squares

    def select_sensing_square(self, uncertain_squares: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # Select the sensing square that provides the most valuable information
        max_info_gain = -float('inf')
        best_square = None
        for square in uncertain_squares:
            info_gain = self.calculate_information_gain(square, move_actions, seconds_left)
            if info_gain > max_info_gain:
                max_info_gain = info_gain
                best_square = square
        return best_square

    def calculate_information_gain(self, square: Square, move_actions: List[chess.Move], seconds_left: float) -> float:
        # Calculate the potential information gain of sensing a specific square
        info_gain = 0
        for move in move_actions:
            if move.to_square == square or move.from_square == square:
                info_gain += 1

        # Incorporate opponent move patterns
        opponent_move_weight = 1 + len(self.opponent_moves) / 10  # Adjust this value as needed
        for opponent_move in self.opponent_moves:
            if opponent_move.to_square == square or opponent_move.from_square == square:
                info_gain *= opponent_move_weight

        # Incorporate remaining time
        time_weight = 1 + (seconds_left / 60)  # Adjust this value as needed
        info_gain *= time_weight

        return info_gain

    def sense_center_squares(self, sense_actions: List[Square]) -> Optional[Square]:
        center_squares = [chess.D4, chess.E4, chess.D5, chess.E5]
        valid_center_squares = [square for square in sense_actions if square in center_squares]
        if valid_center_squares:
            return random.choice(valid_center_squares)
        else:
            return random.choice(sense_actions)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.possible_states = compare_state_window(self.possible_states, sense_result)
        if sense_result:
            self.sensing_history.append(sense_result[len(sense_result) // 2][0])  # Store the center square of the sensing result

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        num_states = len(self.possible_states)
        if num_states > 2000:
            self.possible_states = set(random.sample(self.possible_states, 2000))
            num_states = 2000

        # Use Stockfish to evaluate moves for each possible state
        evaluated_moves = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            result = self.engine.play(board, chess.engine.Limit(time=min(seconds_left / 2, 5/num_states), depth=15))
            if result.move in move_actions:
                evaluated_moves.append((result.move, result.info["score"].relative.score(mate_score=10000)))

        # Incorporate opponent move patterns and game phase
        for move, score in evaluated_moves:
            if move in self.opponent_moves:
                score *= 0.8  # Penalize moves that the opponent has played before
            if self.is_opening_phase():
                if self.is_developing_move(move):
                    score *= 1.2  # Encourage developing moves in the opening
            elif self.is_endgame_phase():
                if self.is_pawn_move(move):
                    score *= 1.1  # Slightly favor pawn moves in the endgame

        # Choose the move with the highest average evaluation score
        if evaluated_moves:
            best_move = max(evaluated_moves, key=lambda x: x[1])[0]
            return best_move
        else:
            # If no valid moves are found, return a random move from move_actions
            return random.choice(move_actions)

    def is_opening_phase(self) -> bool:
        # Define your own criteria for the opening phase
        return len(self.move_history) < 20

    def is_endgame_phase(self) -> bool:
        # Define your own criteria for the endgame phase
        material_count = sum(c.pop_count() for fen in self.possible_states for c in chess.Board(fen).piece_maps().values())
        return material_count < 12

    def is_developing_move(self, move: chess.Move) -> bool:
        # Define your own criteria for developing moves
        piece = chess.Board().piece_at(move.from_square)
        return piece is not None and (piece.piece_type == chess.KNIGHT or piece.piece_type == chess.BISHOP)

    def is_pawn_move(self, move: chess.Move) -> bool:
        piece = chess.Board().piece_at(move.from_square)
        return piece is not None and piece.piece_type == chess.PAWN

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
        captured_opponent_piece: bool, capture_square: Optional[Square]):
        if requested_move != taken_move:
            self.possible_states = [fen for fen in self.possible_states if chess.Board(fen).is_legal(taken_move)]
        
        if captured_opponent_piece:
            self.possible_states = [fen for fen in self.possible_states if chess.Board(fen).piece_at(capture_square) is None]

        # Update the opponent's move history
        if taken_move is not None:
            self.opponent_moves.append(taken_move)
            self.move_history.append(taken_move)

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
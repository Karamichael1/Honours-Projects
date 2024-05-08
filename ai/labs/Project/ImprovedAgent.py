import chess
import chess.engine
import random
from reconchess import *
from collections import defaultdict
import numpy as np
from typing import List, Tuple, Optional

from dataclasses import dataclass

@dataclass
class SenseConfig:
    boards_per_centipawn: float = 50
    expected_outcome_coef: float = 1.0
    worst_outcome_coef: float = 0.2
    outcome_variance_coef: float = -0.3
    score_variance_coef: float = 0.15

@dataclass
class MoveConfig:
    mean_score_factor: float = 0.7
    min_score_factor: float = 0.3
    max_score_factor: float = 0.0
    threshold_score: float = 10
    sense_by_move: bool = False
    force_promotion_queen: bool = True
    sampling_exploration_coef: float = 1_000.0
    move_sample_rep_limit: int = 100

@dataclass
class ScoreConfig:
    search_depth: int = 5
    capture_king_score: int = 1_000_000
    into_check_score: int = -1_000_000
    capture_score: int = 500_000
    hanging_material_penalty_ratio: float = 0.1
    rook_bonus: int = 5  # Bonus for rook presence on the board
    reward_attacker: int = 2

@dataclass
class TimeConfig:
    turns_to_plan_for: int = 16
    min_time_for_turn: float = 3.0
    max_time_for_turn: float = 40.0
    time_for_sense: float = 0.7
    time_for_move: float = 0.3
    calc_time_per_move: float = 0.005
class ImprovedAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.possible_states = set()
        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish', setpgrp=True)
        self.score_cache = dict()
        self.boards_in_cache = set()
        self.board_sample_priority = defaultdict(set)
        self.sense_config = SenseConfig()
        self.move_config = MoveConfig()
        self.score_config = ScoreConfig()
        self.time_config = TimeConfig()

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color
        self.possible_states = {board.fen()}

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        if self.color == chess.WHITE and self.board.fullmove_number == 1:
            # If playing as white and it's the first move, no need to update possible states
            return

        if captured_my_piece:
            # Opponent captured one of our pieces
            self.possible_states = {
                fen for fen in self.possible_states
                if any(chess.Board(fen).piece_at(sq) is None for sq in chess.SQUARES if self.board.piece_at(sq) is not None)
            }
        else:
            # Opponent did not capture any of our pieces
            self.possible_states = {
                fen for fen in self.possible_states
                if all(chess.Board(fen).piece_at(sq) == self.board.piece_at(sq) for sq in chess.SQUARES if self.board.piece_at(sq) is not None)
            }

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        if len(self.possible_states) == 1:
            return None

        if seconds_left < 10:
            return self.sense_min_states(sense_actions, move_actions, seconds_left)
        else:
            return self.sense_max_outcome(sense_actions, move_actions, seconds_left)

    def sense_min_states(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        sample_size = min(len(self.possible_states), 2500)
        board_sample = random.sample(self.possible_states, sample_size)

        num_occurances = defaultdict(lambda: defaultdict(float))
        sense_results = defaultdict(lambda: defaultdict(set))
        for board_fen in board_sample:
            board = chess.Board(board_fen)
            for square in sense_actions:
                sense_result = sense_masked_bitboards(board, square)
                num_occurances[square][sense_result] += 1
                sense_results[square][board_fen] = sense_result

        expected_set_reduction = {
            square:
                len(self.possible_states) *
                (1 - (1 / len(board_sample) ** 2) *
                 sum([num_occurances[square][sense_result] ** 2 for sense_result in sense_results[square].values()]))
            for square in sense_actions
        }

        max_sense_score = max(expected_set_reduction.values())
        sense_choice = random.choice(
            [square for square, score in expected_set_reduction.items() if abs(score - max_sense_score) < 1e-5]
        )
        return sense_choice

    def sense_max_outcome(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        sample_size = min(len(self.possible_states), 2500)
        board_sample = random.sample(self.possible_states, sample_size)

        sense_scores = {}
        for square in sense_actions:
            sense_result = sense_masked_bitboards(board_sample, square)
            outcome_scores = []
            for sense_result_board in sense_result:
                op_score = self.score_cache.get(sense_result_board, None)
                if op_score is None:
                    op_score = self.evaluate_board(sense_result_board)
                    self.score_cache[sense_result_board] = op_score
                outcome_scores.append(op_score)
            sense_scores[square] = (
                np.mean(outcome_scores) * self.sense_config.expected_outcome_coef +
                np.min(outcome_scores) * self.sense_config.worst_outcome_coef +
                np.std(outcome_scores) * self.sense_config.outcome_variance_coef
            )

        return max(sense_scores, key=sense_scores.get)

    def evaluate_board(self, board_fen: str) -> float:
        board = chess.Board(board_fen)
        result = self.engine.analyse(board, chess.engine.Limit(depth=self.score_config.search_depth))
        score = result["score"].white().score(mate_score=10000)
        return score

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        self.possible_states = compare_state_window(self.possible_states, sense_result)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        if len(self.possible_states) == 1:
            board = chess.Board(next(iter(self.possible_states)))
            return self.engine.play(board, chess.engine.Limit(time=seconds_left)).move

        move_scores = defaultdict(RunningEst)
        for board_fen in self.possible_states:
            board = chess.Board(board_fen)
            op_score = self.score_cache.get(board_fen, None)
            if op_score is None:
                op_score = self.evaluate_board(board_fen)
                self.score_cache[board_fen] = op_score
            for move in move_actions:
                if move in board.legal_moves:
                    board_copy = board.copy()
                    board_copy.push(move)
                    move_score = self.score_cache.get(board_copy.fen(), None)
                    if move_score is None:
                        move_score = self.evaluate_board(board_copy.fen())
                        self.score_cache[board_copy.fen()] = move_score
                    move_scores[move].update(move_score - op_score)

        compound_score = {
            move: (
                    est.minimum * self.move_config.min_score_factor +
                    est.maximum * self.move_config.max_score_factor +
                    est.average * self.move_config.mean_score_factor
            ) for move, est in move_scores.items()
        }

        highest_score = max(compound_score.values())
        threshold_score = highest_score - self.move_config.threshold_score
        move_options = [move for move, score in compound_score.items() if score >= threshold_score]
        move_choice = random.choice(move_options)

        return move_choice

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
        captured_opponent_piece: bool, capture_square: Optional[Square]):
        if requested_move != taken_move:
            self.possible_states = [fen for fen in self.possible_states if chess.Board(fen).is_legal(taken_move)]
        
        if captured_opponent_piece:
            self.possible_states = [fen for fen in self.possible_states if chess.Board(fen).piece_at(capture_square) is None]

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        self.engine.quit()
        


def make_move(fen_string, move_string):
    # Apply a move to a FEN string and return the resulting FEN string
    board = chess.Board(fen_string)
    move = chess.Move.from_uci(move_string)

    board.push(move)
    return board.fen()

def generate_next_moves(fen_string):
    # Generate all possible next moves from a FEN string
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
    # Generate all possible next moves that capture a piece at the specified square
    board = chess.Board(fen_string)
    target_square = chess.parse_square(capture_square)
    capture_moves = []
    
    for move in board.legal_moves:
        if move.to_square == target_square and board.is_capture(move):
            uci = move.uci() 
            capture_moves.append(uci)
    
    return sorted(capture_moves)

def generate_next_positions(fen_string, possible_moves):
    # Generate all possible next positions from a FEN string and a list of possible moves
    fen_possibilites = []
    for possible_move in possible_moves:
        fen_possibilites.append(make_move(fen_string, possible_move))

    return sorted(fen_possibilites)

def compare_state_window(fen_states, sense_result):
    # Filter out FEN states that are inconsistent with the sensing result
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
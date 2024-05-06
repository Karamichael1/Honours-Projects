import chess
import chess.engine
import random
from typing import List, Tuple
from collections import Counter

class RandomSensing(Player):
    def __init__(self):
        # Initialize the agent's color, possible board states, and the Stockfish engine
        self.color = None
        self.possible_states = []
        self.engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)

    def handle_game_start(self, color: chess.Color, board: chess.Board, opponent_name: str):
        # Store the agent's color and the initial board state
        self.color = color
        self.possible_states = [board.fen()]

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[chess.Square]):
        # Update the possible board states based on whether the opponent captured a piece or not
        new_states = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            if captured_my_piece:
                new_states.extend(self.filter_states_by_capture(board, capture_square))
            else:
                new_states.extend(self.filter_states_by_non_capture(board))
        self.possible_states = new_states

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # Select a random, non-edge square to sense
        valid_sense_actions = [square for square in sense_actions if not self.is_edge_square(square)]
        return random.choice(valid_sense_actions) if valid_sense_actions else None

    def is_edge_square(self, square: chess.Square) -> bool:
        # Check if a square is on the edge of the board
        row, col = chess.square_rank(square), chess.square_file(square)
        return row in (0, 7) or col in (0, 7)

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # Update the possible board states based on the sense result
        new_states = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            if self.board_matches_sense_result(board, sense_result):
                new_states.append(fen)
        self.possible_states = new_states

    def board_matches_sense_result(self, board: chess.Board, sense_result: List[Tuple[Square, Optional[chess.Piece]]]) -> bool:
        # Check if the board matches the sense result
        for square, piece in sense_result:
            if board.piece_at(square) != piece:
                return False
        return True

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        # Select the most common move among the possible states using Stockfish
        if not self.possible_states:
            return None

        # Limit the number of possible states to 10000 if there are more
        if len(self.possible_states) > 10000:
            self.possible_states = random.sample(self.possible_states, 10000)

        # Calculate the time limit for Stockfish based on the number of states
        time_per_move = seconds_left / len(self.possible_states)
        moves = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            result = self.engine.play(board, chess.engine.Limit(time=time_per_move, depth=10))
            moves.append(result.move.uci())

        move_counts = Counter(moves)
        most_common_move = max(move_counts, key=move_counts.get)
        return chess.Move.from_uci(most_common_move)

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
                           captured_opponent_piece: bool, capture_square: Optional[chess.Square]):
        # Update the possible board states based on the move that was actually taken
        if taken_move is None:
            return

        new_states = []
        for fen in self.possible_states:
            board = chess.Board(fen)
            board.push(taken_move)
            if captured_opponent_piece and capture_square is not None:
                if board.piece_at(capture_square) is None:
                    new_states.append(board.fen())
            else:
                new_states.append(board.fen())
        self.possible_states = new_states

    def filter_states_by_capture(self, board: chess.Board, capture_square: Optional[chess.Square]) -> List[str]:
        # Filter the possible board states based on a capture move
        new_states = []
        for move in board.legal_moves:
            if board.is_capture(move) and (capture_square is None or move.to_square == capture_square):
                new_board = board.copy()
                new_board.push(move)
                new_states.append(new_board.fen())
        return new_states

    def filter_states_by_non_capture(self, board: chess.Board) -> List[str]:
        # Filter the possible board states based on a non-capture move
        new_states = []
        for move in board.legal_moves:
            if not board.is_capture(move):
                new_board = board.copy()
                new_board.push(move)
                new_states.append(new_board.fen())
        return new_states

    def handle_game_end(self, winner_color: Optional[chess.Color], reason: str, game_history: GameHistory):
        # Quit the Stockfish engine when the game ends
        self.engine.quit()
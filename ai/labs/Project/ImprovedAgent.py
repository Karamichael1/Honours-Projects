import chess
import chess.engine
import random
from reconchess import Player, Color, GameHistory, WinReason, Square
from typing import List, Tuple, Optional
# move sequences from white's perspective, flipped at runtime if playing as black
QUICK_ATTACKS = [
    # four move mates
    [chess.Move(chess.E2, chess.E4), chess.Move(chess.F1, chess.C4), chess.Move(chess.D1, chess.H5), chess.Move(
        chess.C4, chess.F7), chess.Move(chess.F7, chess.E8), chess.Move(chess.H5, chess.E8)],
]


def flipped_move(move):
    def flipped(square):
        return chess.square(chess.square_file(square), 7 - chess.square_rank(square))

    return chess.Move(from_square=flipped(move.from_square), to_square=flipped(move.to_square),
                      promotion=move.promotion, drop=move.drop)

class ImprovedAgent(Player):
    def __init__(self):
        self.board = None
        self.color = None
        self.piece_captured = None
        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', setpgrp=True)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        self.board = board
        self.color = color
        if color == chess.BLACK:
            self.move_sequence = list(map(flipped_move, self.move_sequence))

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):        
        # if the opponent captured our piece, remove it from our board.
        self.piece_captured = capture_square
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)


    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # if our piece was just captured, sense where it was captured
        if self.piece_captured:
            return self.piece_captured
        
        # if we might capture a piece when we move, sense where the capture will occur
        future_move = self.choose_move(move_actions, seconds_left)
        if future_move is not None and self.board.piece_at(future_move.to_square) is not None:
            return future_move.to_square
        
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            return enemy_king_square
    
        num_pieces = len(self.board.piece_map())
        if num_pieces > 32:
            game_phase = "opening"
        elif num_pieces > 16:
            game_phase = "middlegame"
        else:
            game_phase = "endgame"

        # prioritize sensing based on the game phase
        if game_phase == "opening":
            # focus on sensing central squares and key positions
            central_squares = [
                chess.D4, chess.E4, chess.D5, chess.E5,
                chess.C4, chess.F4, chess.C5, chess.F5,
                chess.C3, chess.D3, chess.E3, chess.F3,
                chess.C6, chess.D6, chess.E6, chess.F6
            ]
            for square in central_squares:
                if square in sense_actions:
                    return square

        elif game_phase == "middlegame":
            # focus on sensing squares critical for control, defense, and attack
            important_squares = []
            for square in sense_actions:
                if self.board.is_attacked_by(not self.color, square):
                    important_squares.append(square)
                elif self.board.attackers(self.color, square):
                    important_squares.append(square)
            if important_squares:
                return random.choice(important_squares)

        else:  # endgame
            # prioritize sensing squares crucial for the endgame position
            enemy_king_square = self.board.king(not self.color)
            if enemy_king_square:
                return enemy_king_square

            pawn_squares = []
            for square in sense_actions:
                piece = self.board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN:
                    pawn_squares.append(square)
            if pawn_squares:
                return random.choice(pawn_squares)

        # if no specific strategy applies, randomly choose a sense action
        # but don't sense on a square where our pieces are located
        for square, piece in self.board.piece_map().items():
            if piece.color == self.color:
                sense_actions.remove(square)
        if sense_actions:
            return random.choice(sense_actions)

        return None

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        # add the pieces in the sense result to our board
        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        while len(self.move_sequence) > 0 and self.move_sequence[0] not in move_actions:
            self.move_sequence.pop(0)
        if len(self.move_sequence) > 0:
            return self.move_sequence.pop(0)
        # if we might be able to take the king, try to
        enemy_king_square = self.board.king(not self.color)
        if enemy_king_square:
            # if there are any ally pieces that can take king, execute one of those moves
            enemy_king_attackers = self.board.attackers(self.color, enemy_king_square)
            if enemy_king_attackers:
                attacker_square = enemy_king_attackers.pop()
                return chess.Move(attacker_square, enemy_king_square)
        # otherwise, try to move with the stockfish chess engine
        try:
            self.board.turn = self.color
            self.board.clear_stack()
            result = self.engine.play(self.board, chess.engine.Limit(time=0.5))
            return result.move
        except chess.engine.EngineTerminatedError:
            None
        except chess.engine.EngineError:
            None
        # if all else fails, pass
        return None

    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
        captured_opponent_piece: bool, capture_square: Optional[Square]):
        # if a move was executed, apply it to our board
        if taken_move is not None:
            self.board.push(taken_move)

    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason],
        game_history: GameHistory):
        try:
            # if the engine is already terminated then this call will throw an exception
            self.engine.quit()
        except chess.engine.EngineTerminatedError:
            pass
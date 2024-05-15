import chess
import chess.engine
import random
from reconchess import utilities
from reconchess import *
from collections import Counter
import math
import matplotlib.pyplot as plt

class ImprovedAgent(Player):
    
    # DONE
    def __init__(self):
        self.board = None
        self.color = None
        self.num_randoms = 0
        self.possible_boards = set()
        self.non_edge_squares = []
        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', setpgrp=True, timeout = 30)

        self.sensed_squares = set()
        self.last_sensed_turn = {square: 0 for square in range(64)}
        self.my_piece_captured_square = None
        self.turn = 0

    # DONE
    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        # initialize the agent's state at the start of the game
        self.board = board
        self.color = color
        for square in range(64):
            if square // 8 != 0 and square // 8 != 7:
                if square % 8 != 0 and square % 8 != 7:
                    self.non_edge_squares.append(square)
        self.possible_boards.add(self.board.fen())

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):

        # if white, skip 1st method call
        if (self.color and chess.STARTING_FEN==self.board.fen()):
            return
        
        if captured_my_piece:
            self.board.remove_piece_at(capture_square)
        
        new_possible_boards = set() 
        self.my_piece_captured_square = capture_square

        # for each possible board
        for fen in self.possible_boards:
            board = chess.Board(fen)

            moves = generate_next_moves(board)
            # find all possible moves that could have led to the capture
            for move in moves:
                if capture_square is not None and move.to_square == capture_square:
                    board.push(move)
                    new_possible_boards.add(board.fen())
                    board.pop()   
                elif capture_square is None:
                    board.push(move)
                    new_possible_boards.add(board.fen())
                    board.pop()  

        if len(new_possible_boards) == 0:
            new_possible_boards.add(self.board)

        self.possible_boards = new_possible_boards

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        
        self.turn += 1
        # Check for Scholar's Mate in the first 4 turns
        if self.turn <= 4:  
            if self.color == chess.WHITE:
                if self.turn == 1:
                    return chess.F2 
                elif self.turn == 3:
                    return chess.F7
            else:
                if self.turn == 2:
                    return chess.E7
                elif self.turn == 4:
                    return chess.F7
            
        if self.my_piece_captured_square:
            # Check if the captured square is on the edge
            row = self.my_piece_captured_square // 8
            col = self.my_piece_captured_square % 8
            if row == 0 or row == 7 or col == 0 or col == 7:
                # If on the edge, find a square adjacent or one square away
                for square in sense_actions:
                    square_row = square // 8
                    square_col = square % 8
                    row_diff = abs(square_row - row)
                    col_diff = abs(square_col - col)
                    if (row_diff <= 1 and col_diff <= 1) and (row_diff + col_diff > 0):
                        return square
            else:
                return self.my_piece_captured_square
        
        sense_action = self.adapted_entropy(self.possible_boards, not self.color)
        return sense_action

    def adapted_entropy(self, possible_boards, player):
        # Cache board objects for each FEN
        board_cache = {fen: chess.Board(fen) for fen in possible_boards}

        # Calculate entropy for each square
        square_entropies = {}
        for square in range(64):
            piece_counts = Counter(board_cache[fen].piece_at(square) for fen in possible_boards)
            total = sum(piece_counts.values())
            entropy = -sum(count/total * math.log2(count/total) if count > 0 else 0 for count in piece_counts.values())
            square_entropies[square] = entropy

        # Calculate threat weight for each square
        square_threats = {}
        for square in range(64):
            threat_weight = sum(
                sum(self.piece_value(board_cache[fen].piece_at(attacker_square).piece_type)
                    for attacker_square in board_cache[fen].attackers(player, square)
                    if board_cache[fen].piece_at(attacker_square) is not None)
                for fen in possible_boards
            )
            square_threats[square] = threat_weight

        # Compute aggregate entropy for each 3x3 region
        region_entropies = {}
        for center_square in self.non_edge_squares:
            region = [center_square - 9, center_square - 8, center_square - 7,
                    center_square - 1, center_square, center_square + 1,
                    center_square + 7, center_square + 8, center_square + 9]
            region_entropy = sum(square_entropies[square] for square in region)
            region_threat = sum(square_threats[square] for square in region)
            
            # Apply penalty for previously sensed squares
            penalty = sum(0.9 ** (self.turn - self.last_sensed_turn[square])
                        for square in region if square in self.sensed_squares)
            
            region_entropies[center_square] = region_entropy + 0.01 * region_threat - penalty

        best_square = max(region_entropies, key=region_entropies.get)
        
        # Update sensed squares and last sensed turn
        self.sensed_squares.add(best_square)
        self.last_sensed_turn[best_square] = self.turn
        
        return best_square
    
    def piece_value(self, piece_type):
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 100 # We don't want to capture the king
        }
        return values.get(piece_type, 0)

    # DONE
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        new_possible_boards = set()

        for square, piece in sense_result:
            self.board.set_piece_at(square, piece)


        # for each possible board
        for fen in self.possible_boards:
            match = True
            board = chess.Board(fen)

            # for each window piece
            for window_position, window_piece in sense_result:
                                    
                # if there is no piece in the window positon
                if window_piece is None:
                    # but the board has a piece on the board at that window positon
                    if board.piece_at(window_position) is not None:
                        match = False
                        break
                    
                # if there is a piece in the window positon
                else:
                    # but the board has no piece on the board at that window positon
                    if board.piece_at(window_position) is None:
                        match = False
                        break
                    
                    # but the board and window do not match at that window position
                    if not board.piece_at(window_position) == window_piece:
                        match = False
                        break

            # if verification passed keep the board
            if match:
                new_possible_boards.add(board.fen())
        
        self.possible_boards = new_possible_boards

    # TEMP DONE
    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:
        
        # if there are no more boards
        if len(self.possible_boards) == 0:
            move = random.choice(move_actions)
            if self.num_randoms == 0:
                self.num_randoms = 1

            return move

        if len(self.possible_boards) > 10000:
            possible_boards = set(random.sample(self.possible_boards, 10000))
        else:
            possible_boards = self.possible_boards.copy()

        possible_moves = []
        # for each possible board
        for fen in possible_boards:
        # for fen in self.possible_boards:

            board = chess.Board(fen)
            king_square = board.king(not self.color)
            attackers_on_king_square = board.attackers(self.color, king_square)

            if attackers_on_king_square:
                attacker_square = attackers_on_king_square.pop()

                final_move = chess.Move(attacker_square, king_square)
                if final_move in move_actions:
                    possible_moves.append(final_move.uci())

            # if the king is not attacked
            else:
                try:
                    board.turn = self.color
                    board.clear_stack()

                    # get the best move from stockfish
                    move = self.engine.play(board, chess.engine.Limit(time=10/len(possible_boards), depth = 1)).move
                    if move in move_actions:
                        possible_moves.append(move.uci())
                except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                    self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', setpgrp=True, timeout = 30)
                except chess.IllegalMoveError:
                    possible_moves.append(random.choice(move_actions).uci())

        # if there are no possible moves
        if not possible_moves:
            move = random.choice(move_actions)
            return move
        
        # get the most occuring move
        move_counts = Counter(sorted(possible_moves))
        move = max(move_counts, key=move_counts.get)

        return chess.Move.from_uci(move)
    
    # OPTIMIZE - done i think
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move],
        captured_opponent_piece: bool, capture_square: Optional[Square]):
        # # Update the possible states based on the move result

        new_possible_boards = set()
        #  updating so 1st turn works
        if (self.color and chess.STARTING_FEN==self.board.fen()):
            self.board.push(taken_move)

        # if a move was taken
        if taken_move is not None:
            for fen in self.possible_boards:
                board = chess.Board(fen)

                moves = generate_next_moves(board)                
                # Check if the taken move is pseudo-legal
                if taken_move in moves:
                    board.push(taken_move)
                    new_possible_boards.add(board.fen())
                    board.pop()
        
        # if a move was not taken
        else:
            # if the requested move was none
            if requested_move is None:
                new_possible_boards = self.possible_boards.copy()
            
            # if the requested move was a different move
            else:
                for fen in self.possible_boards:
                    board = chess.Board(fen)

                    moves = generate_next_moves(board)                

                    if requested_move not in moves:
                        board.push(requested_move)
                        new_possible_boards.add(board.fen())
                        board.pop()

        self.possible_boards = new_possible_boards


    # DONE 
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        # Clean up the chess engine process at the end of the game
        self.engine.quit()


def generate_next_moves(board):

    # define an empty list of moves
    moves = [chess.Move.null()]

    # for every possible move, add it to the list
    for move in board.generate_pseudo_legal_moves():
        moves.append(move)

    # check possible castle moves
    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        # if they are legal castle moves and not already in the moves list, add them to moves
        if not utilities.is_illegal_castle(board, move):
            if move not in moves:
                moves.append(move)

    for move in utilities.pawn_capture_moves_on(board):
        moves.append(move)

    return moves

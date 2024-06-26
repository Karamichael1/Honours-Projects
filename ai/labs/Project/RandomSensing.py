import chess
import chess.engine
import random
from reconchess import utilities
from reconchess import *
from collections import Counter

class RandomSensingAgent(Player):
    
    def __init__(self):
        self.board = None
        self.color = None
        self.possible_boards = set()
        self.non_edge_squares = []
        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', timeout = 30)

    def handle_game_start(self, color: Color, board: chess.Board, opponent_name: str):
        # initialize the agent's state at the start of the game
        self.board = board
        self.color = color
        # gets the non edge squares
        for square in range(64):
            if square // 8 != 0 and square // 8 != 7:
                if square % 8 != 0 and square % 8 != 7:
                    self.non_edge_squares.append(square)
        # records the intial board
        self.possible_boards.add(self.board.fen())

    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        
        # if white, skip 1st method call
        if (self.color and chess.STARTING_FEN==self.board.fen()):
            return
        
        new_possible_boards = set() 

        # for each possible board
        for fen in self.possible_boards:
            board = chess.Board(fen)

            # get all possible moves
            moves = generate_next_moves(board)
            for move in moves:
                if move in board.pseudo_legal_moves:
                    # if there is a capture
                    if capture_square is not None and move.to_square is not None and move.to_square == capture_square:
                        board.push(move)
                        new_possible_boards.add(board.fen())
                        board.pop()   
                    # if there is no capture
                    elif capture_square is None:
                        board.push(move)
                        new_possible_boards.add(board.fen())
                        board.pop()  

        self.possible_boards = new_possible_boards

    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # return a random non edge square
        sense_action = random.choice(self.non_edge_squares)

        while sense_action not in sense_actions:
            sense_action = random.choice(self.non_edge_squares)

        return sense_action

    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        new_possible_boards = set()

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

    def choose_move(self, move_actions: List[chess.Move], seconds_left: float) -> Optional[chess.Move]:

        # if there are no more boards return a random move
        if len(self.possible_boards) == 0:
            move = random.choice(move_actions)
            return move

        # if there are more than 10000 boards, randomly sample 10000
        if len(self.possible_boards) > 10000:
            self.possible_boards = set(random.sample(self.possible_boards, 10000))

        possible_moves = []

        # for each possible board
        for fen in self.possible_boards:
            board = chess.Board(fen)

            # attempt to capture the king
            king_square = board.king(not self.color)
            if king_square is not None:
                attackers_on_king_square = board.attackers(self.color, king_square)

                if len(attackers_on_king_square) > 0:
                    attacker_square = attackers_on_king_square.pop()

                    final_move = chess.Move(attacker_square, king_square)
                    if final_move in move_actions:
                        possible_moves.append(final_move.uci())

            # cant capture the king
            else:
                # get best move from stockfish
                try:
                    board.turn = self.color
                    board.clear_stack()
                    move = self.engine.play(board, chess.engine.Limit(time=10/len(self.possible_boards), depth = 1)).move
                    if move in move_actions:
                        possible_moves.append(move.uci())
                except (chess.engine.EngineTerminatedError, chess.engine.EngineError):
                    self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', timeout = 30)
                except chess.IllegalMoveError:
                    possible_moves.append(random.choice(move_actions).uci())

        # if there are no possible moves do a random move
        if not possible_moves:
            move = random.choice(move_actions)
            return move
        
        # get the most popular move
        move_counts = Counter(sorted(possible_moves))
        move = max(move_counts, key=move_counts.get)

        return chess.Move.from_uci(move)
    
    def handle_move_result(self, requested_move: Optional[chess.Move], taken_move: Optional[chess.Move], captured_opponent_piece: bool, capture_square: Optional[Square]):

        new_possible_boards = set()

        #  updating so 1st turn works
        if (self.color and chess.STARTING_FEN==self.board.fen()) and taken_move is not None:
            self.board.push(taken_move)

        # if a move was taken
        if taken_move is not None:
            for fen in self.possible_boards:
                board = chess.Board(fen)

                moves = generate_next_moves(board)                
                # Check if the taken move is pseudo-legal
                if taken_move in moves and taken_move in board.pseudo_legal_moves:
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
                        new_possible_boards.add(board.fen())

        self.possible_boards = new_possible_boards

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
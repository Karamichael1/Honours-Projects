import chess
import chess.engine
import random
from reconchess import utilities
from reconchess import *
from collections import Counter

class RandomSensingAgent(Player):
    
    # DONE
    def __init__(self):
        self.board = None
        self.color = None
        self.my_king_position = None
        self.opponent_king_position = None
        self.possible_boards = set()
        self.non_edge_squares = []

        self.engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish.exe', setpgrp=True)

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


    # OPTIMIZE - done i think
    def handle_opponent_move_result(self, captured_my_piece: bool, capture_square: Optional[Square]):
        # if white, skip 1st method call
        if (self.color and chess.STARTING_FEN==self.board.fen()):
            return
        
        new_possible_boards = set() 

        # oponent has made a capture
        if captured_my_piece:
            

            # for each possible board
            for fen  in self.possible_boards:
                board = chess.Board(fen)

                # find every possible attacker on that square
                capture_square_attackers = board.attackers(not self.color, capture_square)
                for attacker_square in capture_square_attackers:
                    # perform the attacking move and add it to the possible states
                    board.push(chess.Move(attacker_square, capture_square))
                    new_possible_boards.add(board.fen())
                    board.pop()
                    
        # oponent has not made a capture  
        else:
        

            # for each possible board
            for fen in self.possible_boards:
                board = chess.Board(fen)

                # for each possible move
                for move in board.legal_moves:

                    #  if the move is a capture
                    if board.is_capture(move):
                        continue
                    
                    # the move is now a possible board
                    board.push(move)
                    new_possible_boards.add(board.fen())
                    board.pop()            
                

        self.possible_boards = new_possible_boards
    # DONE
    def choose_sense(self, sense_actions: List[Square], move_actions: List[chess.Move], seconds_left: float) -> Optional[Square]:
        # return a random non edge square

        sense_action = random.choice(self.non_edge_squares)

        while sense_action not in sense_actions:
            sense_action = random.choice(self.non_edge_squares)

        return sense_action

    # DONE
    def handle_sense_result(self, sense_result: List[Tuple[Square, Optional[chess.Piece]]]):
        
        new_possible_boards = set()

        # for each possible board
        for fen in self.possible_boards:
            match = True
            board = chess.Board(fen)

            # for each window piece
            for window_position, window_piece in sense_result:
                
                # temporary, figure out
                if window_piece == 'K':
                    if self.color:
                        
                        print(window_piece)
                        self.my_king_position = window_position
                    else:
                        print(window_piece)
                        self.opponent_king_position = window_position
                
                if window_piece == 'k':
                    if self.color:
                        
                        print(window_piece)
                        self.opponent_king_position = window_position
                    else:
                        
                        print(window_piece)
                        self.my_king_position = window_position
                    
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
        
        
        # if the number of possible boards exceeds 10 000, randomly sample 10 000
        if len(self.possible_boards) > 10000:
            possible_boards = set(random.sample(self.possible_boards, 10000))
        else:
            possible_boards = self.possible_boards

        # if there are no more boards
        if len(self.possible_boards) == 0:
            move = random.choice(move_actions)
            
            return move

        possible_moves = []
        # for each possible board
        for fen in possible_boards:
            board = chess.Board(fen)
        
            # if the opposing king is attacked
            if board.is_check():
                king_square = board.king(not board.turn)
        
                # for each legal move
                for move in board.legal_moves:

                    # if the move is to attack the king
                    if move.to_square == king_square and move in move_actions:
                        possible_moves.append(move.uci())
                        break

            # if the king is not attacked
            else:

                board.turn = self.color
                board.clear_stack()

                # get the best move from stockfish
                move = self.engine.play(board, chess.engine.Limit(time=10/len(possible_boards),depth=10)).move
                if move in move_actions:
                    possible_moves.append(move.uci())

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

        # if a move was taken
        if taken_move is not None:

            #  updating so 1st turn works
            if (self.color and chess.STARTING_FEN==self.board.fen()):
                self.board.push(taken_move)

            
            for fen in self.possible_boards:
                board = chess.Board(fen)
                
                if taken_move in board.legal_moves:
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

                    if requested_move not in board.legal_moves:
                        board.push(requested_move)
                        new_possible_boards.add(board.fen())
                        board.pop()

        self.possible_boards = new_possible_boards

        
    # DONE 
    def handle_game_end(self, winner_color: Optional[Color], win_reason: Optional[WinReason], game_history: GameHistory):
        # Clean up the chess engine process at the end of the game
        self.engine.quit()
    

#   ORDER OF METHOD CALLS
#       handle_opponent_move_result
#       choose_sense
#       handle_sense_result
#       choose_move
#       handle_move_result
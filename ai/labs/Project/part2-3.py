import chess
from reconchess import utilities

# function used to make a move given a fen an move string
def make_move(fen_string, move_string):

    # use chess library to create board
    board = chess.Board(fen_string)
    # use chess library to make move
    move = chess.Move.from_uci(move_string)

    board.push(move)
    return board.fen()

# function used to generate all the possible legal moves given a board state
def generate_next_moves(fen_string):

    # use chess library to create board
    board = chess.Board(fen_string)
    # define an empty list of moves
    moves = []
    
    # for every possible move, add it to the list
    for move in board.generate_pseudo_legal_moves():
        uci = move.uci()
        moves.append(uci)

    # check possible castle moves
    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        # if they are legal castle moves and not already in the moves list, add them to moves
        if not utilities.is_illegal_castle(board, move):
            uci = move.uci()
            if uci not in moves:
                moves.append(uci)

    # add the null move
    moves.append("0000")

    # return the moves sorte alphabetically
    return sorted(moves)

def generate_next_moves_capture(fen_string, capture_square):
    # use chess library to create board
    board = chess.Board(fen_string)
    
    # convert the capture_square to a chess.Square object
    target_square = chess.parse_square(capture_square)
    
    # define an empty list to store capture moves
    capture_moves = []
    
    # iterate over all legal moves
    for move in board.legal_moves:
        # check if the move captures on the target_square
        if move.to_square == target_square and board.is_capture(move):
            uci = move.uci() 
            capture_moves.append(uci)
    
    return sorted(capture_moves)

# generate the next fen stirngs
def generate_next_positions(fen_string, possible_moves):

    fen_possibilites = []
    # get fen string of each move
    for possible_move in possible_moves:
        fen_possibilites.append(make_move(fen_string, possible_move))

    return sorted(fen_possibilites)


if __name__ == "__main__":
    fen_string = input()
    capture_square = input()

    capture_moves = generate_next_moves_capture(fen_string, capture_square)
    
    fen_results = generate_next_positions(fen_string, capture_moves)
    
    for fen_string in fen_results:
        print(fen_string)
        
        
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

# function used to dectect the possible captures
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

def compare_state_window(fen_states, window):
    fen_results = []
    for fen_string in fen_states:
        # Parse the FEN string into a chess board
        board = chess.Board(fen_string)
        
        # Convert the window string to a 2D list
        window_list = [row.split(":") for row in window.split(";")]
        
        # Compare each square in the window with the corresponding square on the board
        match = True
        for item in window_list:
            window_pos = item[0]
            window_piece = item[1]
            board_square = chess.parse_square(window_pos)
            board_piece = board.piece_at(board_square)
            
            if window_piece == "?":
                if board_piece is not None:
                    match = False
                    break
            else:
                if board_piece is None or \
                   (board_piece.color == chess.WHITE and board_piece.symbol().upper() != window_piece) or \
                   (board_piece.color == chess.BLACK and board_piece.symbol().lower() != window_piece):
                    match = False
                    break
        
        if match:
            fen_results.append(fen_string)
    
    return sorted(fen_results)

if __name__ == "__main__":

    num_states = int(input())

    fen_possible_states = []
    for _ in range(num_states):
        fen = input()
        fen_possible_states.append(fen)

    sensing_window = input()


    fen_results = compare_state_window(fen_possible_states, sensing_window)
    for fen_string in fen_results:
        print(fen_string)

   
        
# 3
# 1k6/1ppn4/8/8/8/1P1P4/PN3P2/2K5 w - - 0 32
# 1k6/1ppnP3/8/8/8/1P1P4/PN3P2/2K5 w - - 0 32
# 1k6/1ppn1p2/8/8/8/1P1P4/PN3P2/2K5 w - - 0 32
# c8:?;d8:?;e8:?;c7:p;d7:n;e7:?;c6:?;d6:?;e6:?

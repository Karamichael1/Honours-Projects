import chess
from reconchess import utilities

# function used to display the board given and fen string
def display_board(fen_string):

    # use chess library to create board
    board = chess.Board(fen_string)
    
    # rank = row
    for rank in range(7, -1, -1): 
        # file = column
        for file in range(8):
            
            # get the square at the file and rank
            square = chess.square(file, rank)

            # get the piece at the square
            piece = board.piece_at(square)

            #  if there is not a piece print a blank space else print the piece
            if piece is None:
                print(".", end=" ")
            else:
                # check which players piece it is and print accordinly
                if piece.color == chess.WHITE:
                    print(piece.symbol().upper(), end=" ")
                else:
                    print(piece.symbol().lower(), end=" ")
        print() 

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

if __name__ == "__main__":
    # take in the fen string
    fen_string = input()

    # get all the next possible moves of the state
    moves = generate_next_moves(fen_string)

    # print each move
    for move in moves:
        print(move)
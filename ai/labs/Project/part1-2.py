import chess

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

# function used to make a move given a fen an move string
def make_move(fen_string, move_string):

    # use chess library to create board
    board = chess.Board(fen_string)
    # use chess library to make move
    move = chess.Move.from_uci(move_string)

    # if the move is valid make the move else print invlaid
    board.push(move)
    return board.fen()


def main():
    #  takes in an fen string (representation of the board)
    fen_string = input()

    #  takes in a move
    move_string = input()

    fen_result = make_move(fen_string, move_string)

    if fen_result != 0:
        print(fen_result)
    else:
        print('Invalid Move')

if __name__ == "__main__":
    main()


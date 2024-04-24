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

def main():
    #  takes in an fen string (representation of the board)
    fen_string = input()

    # create the board
    display_board(fen_string)

if __name__ == "__main__":
    main()
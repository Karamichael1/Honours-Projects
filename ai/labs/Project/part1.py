import chess

def display_board(fen_string):
    board = chess.Board(fen_string)
    for rank in range(7, -1, -1): 
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            if piece is None:
                print(".", end=" ")
            else:
                if piece.color == chess.WHITE:
                    print(piece.symbol().upper(), end=" ")
                else:
                    print(piece.symbol().lower(), end=" ")
        print()  
def main():
    fen_string = input()
    display_board(fen_string)

if __name__ == "__main__":
    main()
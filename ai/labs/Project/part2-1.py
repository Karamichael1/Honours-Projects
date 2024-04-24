import chess
from reconchess import utilities

def generate_next_moves(fen):
    board = chess.Board(fen)
    moves = []

    
    for move in board.generate_pseudo_legal_moves():
        uci = move.uci()
        moves.append(uci)

    
    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        if not utilities.is_illegal_castle(board, move):
            uci = move.uci()
            if uci not in moves:
                moves.append(uci)

    moves.append("0000")

    return sorted(moves)

if __name__ == "__main__":
    fen = input()
    moves = generate_next_moves(fen)
    for move in moves:
        print(move)
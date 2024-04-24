import chess
from reconchess import utilities

def generate_next_positions(fen):
    board = chess.Board(fen)
    positions = []

    
    for move in board.generate_pseudo_legal_moves():
        board.push(move)
        positions.append(board.fen())
        board.pop()

    for move in utilities.without_opponent_pieces(board).generate_castling_moves():
        if not utilities.is_illegal_castle(board, move):
            board.push(move)
            positions.append(board.fen())
            board.pop()

 
    board.push(chess.Move.null())
    positions.append(board.fen())
    board.pop()

    return sorted(positions)

if __name__ == "__main__":
    fen = input()
    positions = generate_next_positions(fen)
    for position in positions:
        print(position)
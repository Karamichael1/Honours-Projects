import chess
import chess.engine

def generate_move(fen):
    board = chess.Board(fen)

    # Check if the opposing king is attacked by one of our pieces
    if board.is_check():
        # Find the square of the opposing king
        opposing_king_square = board.king(not board.turn)
        
        # Generate all legal moves
        legal_moves = board.legal_moves

        # Check if any of the legal moves capture the opposing king
        for move in legal_moves:
            if move.to_square == opposing_king_square:
                return move.uci()

    # If the opposing king is not under attack, ask Stockfish for a move
    engine = chess.engine.SimpleEngine.popen_uci('/opt/stockfish/stockfish', setpgrp=True)
    result = engine.play(board, chess.engine.Limit(time=0.5,depth=10))
    engine.quit()

    return result.move.uci()

# Read the FEN string from input
fen = input()

# Generate the move
move = generate_move(fen)

# Print the move
print(move)
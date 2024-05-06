import chess  # type: ignore 
import chess.engine # type: ignore
from collections import Counter


# Load the Stockfish engine
engine = chess.engine.SimpleEngine.popen_uci('stockfish/stockfish', setpgrp=True)

# Read the number of boards
N = int(input())

# Initialize a list to store the moves
moves = []

# Iterate over each board
for _ in range(N):
    # Read the FEN string
    fen = input().strip()
    
    # Create a chess board from the FEN string
    board = chess.Board(fen)
    
    # Check if the opposing king is attacked
    if board.is_check():
        # Find the square of the opposing king
        king_square = board.king(not board.turn)
        
        # Generate legal moves
        legal_moves = board.legal_moves
        
        # Check if any legal move captures the king
        for move in legal_moves:
            if move.to_square == king_square:
                moves.append(move.uci())
                break

    else:
        # Get the best move from Stockfish with a time limit of 0.5 seconds
        result = engine.play(board, chess.engine.Limit(time=0.5,depth=10))
        moves.append(result.move.uci())

# Close the Stockfish engine
engine.quit()

# Count the frequency of each move
move_counts = Counter(moves)

# Find the most common move
most_common_move = max(move_counts, key=move_counts.get)

# Output the move
print(most_common_move)
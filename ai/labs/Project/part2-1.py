import chess

def generate_next_moves(fen):
    board = chess.Board(fen)
    moves = []
    for move in board.generate_pseudo_legal_moves():
        uci = move.uci()
        moves.append(uci)

    if board.has_kingside_castling_rights(chess.WHITE):
        castling_move = 'e1g1'
        if castling_move not in moves:
            moves.append(castling_move)
    if board.has_kingside_castling_rights(chess.BLACK):
        castling_move = 'e8g8'
        if castling_move not in moves:
            moves.append(castling_move)

    
    if board.has_queenside_castling_rights(chess.WHITE):
        castling_move = 'e1c1'
        if castling_move not in moves:
            moves.append(castling_move)
    if board.has_queenside_castling_rights(chess.BLACK):
        castling_move = 'e8c8'
        if castling_move not in moves:
            moves.append(castling_move)

    moves.append('0000')
    return sorted(moves)

if __name__ == "__main__":
    fen = input()
    moves = generate_next_moves(fen)
    for move in moves:
        print(move)
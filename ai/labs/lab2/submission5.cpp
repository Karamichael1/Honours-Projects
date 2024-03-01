#include <iostream>
#include <vector>

using namespace std;

// Function to check if a player has won
char checkWinner(const vector<char>& board) {
    // Check rows
    for (int i = 0; i < 3; ++i) {
        if (board[i * 3] != '.' && board[i * 3] == board[i * 3 + 1] && board[i * 3 + 1] == board[i * 3 + 2]) {
            return board[i * 3];
        }
    }
    // Check columns
    for (int i = 0; i < 3; ++i) {
        if (board[i] != '.' && board[i] == board[i + 3] && board[i + 3] == board[i + 6]) {
            return board[i];
        }
    }
    // Check diagonals
    if (board[0] != '.' && board[0] == board[4] && board[4] == board[8]) {
        return board[0];
    }
    if (board[2] != '.' && board[2] == board[4] && board[4] == board[6]) {
        return board[2];
    }
    // No winner yet
    return '.';
}

// Recursive function to determine the result of the game
char minimax(vector<char>& board, char player) {
    char winner = checkWinner(board);
    if (winner != '.') {
        return winner;
    }

    // Check for draw
    bool isDraw = true;
    for (char cell : board) {
        if (cell == '.') {
            isDraw = false;
            break;
        }
    }
    if (isDraw) {
        return 'D';
    }

    char bestMove = (player == 'X') ? 'O' : 'X';
    char opponent = (player == 'X') ? 'O' : 'X';
    char opponentWin = (player == 'X') ? 'O' : 'X';

    for (int i = 0; i < 9; ++i) {
        if (board[i] == '.') {
            board[i] = player;
            char moveResult = minimax(board, opponent);
            board[i] = '.';

            if (moveResult == player) {
                return player;
            } else if (moveResult == 'D') {
                bestMove = 'D';
            } else if (moveResult == opponentWin && bestMove != 'D') {
                bestMove = opponentWin;
            }
        }
    }
    return bestMove;
}

int main() {
    vector<char> board(9);
    for (int i = 0; i < 9; ++i) {
        cin >> board[i];
    }

    char player = (count(board.begin(), board.end(), 'X') == count(board.begin(), board.end(), 'O')) ? 'X' : 'O';
    char result = minimax(board, player);

    if (result == 'X') {
        cout << "X wins\n";
    } else if (result == 'O') {
        cout << "O wins\n";
    } else {
        cout << "Draw\n";
    }

    return 0;
}

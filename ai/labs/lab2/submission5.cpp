#include <iostream>
#include <limits>
using namespace std;

const int INFINITY = numeric_limits<int>::max();

bool checkWin(const string& board, char playerSymbol) {
    for (int i = 0; i < 3; i++) {
        if (board[i * 3] == playerSymbol && board[i * 3 + 1] == playerSymbol && board[i * 3 + 2] == playerSymbol)
            return true;
    }

    for (int i = 0; i < 3; i++) {
        if (board[i] == playerSymbol && board[i + 3] == playerSymbol && board[i + 6] == playerSymbol)
            return true;
    }

    if (board[0] == playerSymbol && board[4] == playerSymbol && board[8] == playerSymbol)
        return true;
    if (board[2] == playerSymbol && board[4] == playerSymbol && board[6] == playerSymbol)
        return true;

    return false;
}

bool checkDraw(const string& board) {
    for (char c : board) {
        if (c == '.')
            return false;
    }
    return true;
}

string gameState(const string& board) {
    if (checkWin(board, 'x'))
        return "X wins";
    else if (checkWin(board, 'o'))
        return "O wins";
    else if (checkDraw(board))
        return "Draw";
    else
        return "In progress";
}

int minimax(string position, int depth, bool maximizingPlayer) {
    string gs = gameState(position);
    if (depth == 0 || gs != "In progress") {
        if (gs == "X wins")
            return 10;
        else if (gs == "O wins")
            return -10;
        else
            return 0;
    }

    char playerSymbol = maximizingPlayer ? 'x' : 'o';
    int bestScore = maximizingPlayer ? -INFINITY : INFINITY;

    for (int i = 0; i < 9; i++) {
        if (position[i] == '.') {
            position[i] = playerSymbol;
            int score = minimax(position, depth - 1, !maximizingPlayer);
            position[i] = '.';
            if (maximizingPlayer)
                bestScore = max(bestScore, score);
            else
                bestScore = min(bestScore, score);
        }
    }
    return bestScore;
}

int findBestMove(const string& board, bool maximizingPlayer) {
    int bestMove = -1;
    int bestScore = maximizingPlayer ? -INFINITY : INFINITY;

    for (int i = 0; i < 9; i++) {
        if (board[i] == '.') {
            string tempBoard = board;
            tempBoard[i] = maximizingPlayer ? 'x' : 'o';
            int score = minimax(tempBoard, 9, !maximizingPlayer);
            if (maximizingPlayer) {
                if (score > bestScore) {
                    bestScore = score;
                    bestMove = i;
                }
            } else {
                if (score < bestScore) {
                    bestScore = score;
                    bestMove = i;
                }
            }
        }
    }
    return bestMove;
}

int main() {
    string board;
    cin >> board;
    bool Xturn = true; 
    while (gameState(board) == "In progress") {
        int move = findBestMove(board, Xturn);
        board[move] = Xturn ? 'x' : 'o';
        Xturn = !Xturn; 
    }

    string result = gameState(board);
    cout << result << endl;

    return 0;
}

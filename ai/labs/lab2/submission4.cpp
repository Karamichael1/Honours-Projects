#include <iostream>
using namespace std;

bool checkWin(string board, char playerSymbol) {
    
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

bool checkDraw(string board) {
    for (char c : board) {
        if (c == '.')
            return false; 
    }
    return true;
}

string gameState(string board) {
    if (checkWin(board, 'x'))
        return "X wins";
    else if (checkWin(board, 'o'))
        return "O wins";
    else if (checkDraw(board))
        return "Draw";
    else
        return "In progress";
}


int main(){
    string board="";
    cin>>board;
    cout<<gameState(board); 
}

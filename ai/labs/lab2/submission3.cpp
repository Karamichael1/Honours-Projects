#include <iostream>
using namespace std;

string boardOutput(string board,string player,int row,int col){
    int num=0;
    string matrix[3][3];
    for(int i=0;i<3;i++){
        for(int j=0;j<3;j++){
        if(board[num]=='.'){
            matrix[i][j]="_ ";
        }else if(board[num]=='x'){
            matrix[i][j]="x ";
        }else if(board[num]=='o'){
            matrix[i][j]="o ";
        }
        num++;
        }
    if(player=="0"){
    matrix[row][col]="x ";
    }else{
        matrix[row][col]="o ";
    }   
    
}
for(int i=0;i<3;i++){
        for(int j=0;j<3;j++){
        cout<<matrix[i][j];
        }
        cout<<endl;
    }
return "";
}
int main(){
    string player;
    int row;
    int col;
    string board="";
    cin>>board;
    cin>>player;
    cin>>row;
    cin>>col;
    boardOutput(board,player,row,col); 
}

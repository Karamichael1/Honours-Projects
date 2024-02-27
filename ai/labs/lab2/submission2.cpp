#include <iostream>
using namespace std;

string boardOutput(string board){
    for(int i=0;i<9;i++){
        if(board[i]=='.'){
            cout<<"_ ";
        }else if(board[i]=='x'){
            cout<<"x ";
        }else if(board[i]=='o'){
            cout<<"o ";
        }
        if(i%3==2){
            cout<<endl;
        }
        
}
return "";
}
int main(){
    string board="";
    cin>>board;
    boardOutput(board);
}

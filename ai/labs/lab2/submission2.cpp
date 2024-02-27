#include <iostream>
using namespace std;

string boardOutput(string board){
    for(int i=0;i<9;i++){
        if(i%3==2){
            cout<<endl;
        }
        if(board[i]=='.'){
            cout<<"_ ";
        }else if(board[i]=='x'){
            cout<<"x ";
        }else if(board[i]=='o'){
            cout<<"o ";
        }
}
}
int main(){
    string board="";
    cin>>board>>endl;
    string final=boardOutput(board);
}

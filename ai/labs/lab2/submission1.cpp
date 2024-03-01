#include <iostream>
#include <cmath>
#include <utility>
using namespace std;



string nashEquilibrium(int nash[],int size){
string matrix[size][size];
int count=0;
for(int i=0;i<size;i++){
    for(int j=0;j<size;j++){
    matrix[i][j]=nash[count];
    cout<<matrix[i][j];
    count++;
    }
}

return "hello";
}



int main(){
double size;
cin>>size;
int nash[int(pow(size,2.00))];
for(int i=0;i<pow(size,2.00);i++){
    cin>>nash[i];
}
cout<<nashEquilibrium(nash,size);
return 0;
}
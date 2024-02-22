#include <iostream>
using namespace std;

int main()
{
    string input;
    cin >> input;
    int num = 0;
    char gameboard[4][4];
    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            char curr = input[num];
            if (curr == '#')
            {
                gameboard[i][j] = ' ';
            }
            else
            {
                gameboard[i][j] = curr;
            }
            num = num + 1;
        }
    }
    for (int i = 0; i < 4; ++i)
    {
        
        for (int j = 0; j < 4; ++j)
        {
            
            std::cout << gameboard[i][j] << " ";
        }
        
        std::cout << std::endl;
    }
    return 0;
}

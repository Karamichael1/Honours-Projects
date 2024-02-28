#include <iostream>
using namespace std;

int main()
{
    string input;
    // string direction;
    cin >> input;
    // cin >> direction;
    int num = 0;
    char gameboard[4][4];
    int xAxis = -1;
    int yAxis = -1;

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            char curr = input[num++];
            if (curr == '#')
            {
                xAxis = i;
                yAxis = j;
                gameboard[i][j] = '#';
            }
            else
            {
                gameboard[i][j] = curr;
            }
        }
    }
    if (xAxis > 0)
        cout << "UP" << endl;
    if (xAxis < 3)
        cout << "DOWN" << endl;
    if (yAxis > 0)
        cout << "LEFT" << endl;
    if (yAxis < 3)
        cout << "RIGHT" << endl;

    // for (int i = 0; i < 4; i++)
    // {
    //     for (int j = 0; j < 4; j++)
    //     {
    //         if (gameboard[i][j] == '#' && direction == "RIGHT" && j < 3)
    //         {
    //             gameboard[i][j] = gameboard[i][j + 1];
    //             gameboard[i][j + 1] = '#';
    //             goto end;
    //         }
    //         else if (gameboard[i][j] == '#' && direction == "UP" && i > 0)
    //         {
    //             gameboard[i][j] = gameboard[i - 1][j];
    //             gameboard[i - 1][j] = '#';
    //             goto end;
    //         }
    //         else if (gameboard[i][j] == '#' && direction == "LEFT" && j > 0)
    //         {
    //             gameboard[i][j] = gameboard[i][j - 1];
    //             gameboard[i][j - 1] = '#';
    //             goto end;
    //         }
    //         else if (gameboard[i][j] == '#' && direction == "DOWN" && i < 3)
    //         {
    //             gameboard[i][j] = gameboard[i + 1][j];
    //             gameboard[i + 1][j] = '#';
    //             goto end;
    //         }
    //     }
    // }
    // end:

    //     for (int i = 0; i < 4; ++i)
    //     {
    //         for (int j = 0; j < 4; ++j)
    //         {
    //             std::cout << gameboard[i][j] << " ";
    //         }
    //         std::cout << std::endl;
    //     }
   return 0;
}

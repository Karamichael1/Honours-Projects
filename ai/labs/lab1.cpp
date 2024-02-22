#include <iostream>
using namespace std;

int main()
{
    string input;
    string direction;
    cin >> input;
    cin >> direction;
    int num = 0;
    char gameboard[4][4];

    // Initialize gameboard
    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            char curr = input[num++];
            if (curr == '#')
            {
                gameboard[i][j] = '#';
            }
            else
            {
                gameboard[i][j] = curr;
            }
        }
    }

    // Move based on direction
    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            if (gameboard[i][j] == '#' && direction == "RIGHT" && j < 3)
            {
                gameboard[i][j] = gameboard[i][j + 1];
                gameboard[i][j + 1] = '#';
                break;
            }
            else if (gameboard[i][j] == '#' && direction == "UP" && i < 3)
            {
                gameboard[i][j] = gameboard[i + 1][j];
                gameboard[i + 1][j] = '#';
                break;
            }
            else if (gameboard[i][j] == '#' && direction == "LEFT" && j > 0)
            {
                gameboard[i][j] = gameboard[i][j - 1];
                gameboard[i][j - 1] = '#';
                break;
            }
            else if (gameboard[i][j] == '#' && direction == "DOWN" && i > 0)
            {
                gameboard[i][j] = gameboard[i - 1][j];
                gameboard[i - 1][j] = '#';
                break;
            }
        }
    }

    // Print gameboard
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

#include <iostream>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <string>
#include <vector>
#include <cmath>
#include <fstream>
using namespace std;

bool isGoalState(const string &state)
{
    return state == "ABCDEFGHIJKLMNO#";
}

int misplacedTilesHeuristic(const string &state)
{
    int count = 0;
    for (int i = 0; i < state.size(); ++i)
    {
        if (state[i] != '#' && state[i] != "ABCDEFGHIJKLMNO"[i])
        {
            ++count;
        }
    }
    return count;
}

int sumDistanceTiles(const string &state)
{
    int distance = 0;
    for (int i = 0; i < state.size(); ++i)
    {
        if (state[i] != '#')
        {
            int correctX = (state[i] - 'A') / 4;
            int correctY = (state[i] - 'A') % 4;
            int currentX = i / 4;
            int currentY = i % 4;
            distance += abs(correctX - currentX) + abs(correctY - currentY);
        }
    }
    return distance;
}

vector<string> generateNextStates(const string &state)
{
    vector<string> nextStates;
    int emptyIndex = state.find('#');

    int dx[] = {-1, 1, 0, 0};
    int dy[] = {0, 0, -1, 1};
    string directions = "UDLR";

    for (int i = 0; i < 4; ++i)
    {
        int newX = emptyIndex / 4 + dx[i];
        int newY = emptyIndex % 4 + dy[i];
        if (newX >= 0 && newX < 4 && newY >= 0 && newY < 4)
        {
            string nextState = state;
            swap(nextState[emptyIndex], nextState[newX * 4 + newY]);
            nextStates.push_back(nextState);
        }
    }
    return nextStates;
}
int aStarSearch(const string &initialState)
{
    priority_queue<pair<int, string>, vector<pair<int, string>>, greater<pair<int, string>>> pq;
    unordered_map<string, int> costSoFar;

    pq.push({sumDistanceTiles(initialState), initialState});
    costSoFar[initialState] = 0;

    while (!pq.empty())
    {
        string currentState = pq.top().second;
        int currentCost = costSoFar[currentState] + sumDistanceTiles(currentState);
        pq.pop();

        if (isGoalState(currentState))
        {
            return costSoFar[currentState];
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto &nextState : nextStates)
        {
            int newCost = costSoFar[currentState] + 1;
            if (costSoFar.find(nextState) == costSoFar.end() || newCost < costSoFar[nextState])
            {
                costSoFar[nextState] = newCost;
                int priority = newCost + sumDistanceTiles(nextState);
                pq.push({priority, nextState});
            }
        }
    }

    return -1;
}

int bfs(const string &initialState)
{
    int front = 0;
    queue<pair<string, int>> q;
    unordered_set<string> visited;

    q.push({initialState, 0});
    visited.insert(initialState);

    while (!q.empty())
    {
        string currentState = q.front().first;
        int cost = q.front().second;
        q.pop();

        if (isGoalState(currentState))
        {
            return front;
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto &nextState : nextStates)
        {
            if (visited.find(nextState) == visited.end())
            {
                q.push({nextState, cost + 1});
                visited.insert(nextState);
                front++;
            }
        }
    }

    return -1;
}
int aStarSearch1(const string &initialState)
{
    int front = 0;
    priority_queue<pair<int, string>, vector<pair<int, string>>, greater<pair<int, string>>> pq;
    unordered_map<string, int> costSoFar;

    pq.push({misplacedTilesHeuristic(initialState), initialState});
    costSoFar[initialState] = 0;

    while (!pq.empty())
    {
        string currentState = pq.top().second;
        int currentCost = costSoFar[currentState] + misplacedTilesHeuristic(currentState);
        pq.pop();

        if (isGoalState(currentState))
        {
            return front;
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto &nextState : nextStates)
        {
            int newCost = costSoFar[currentState] + 1;
            if (costSoFar.find(nextState) == costSoFar.end() || newCost < costSoFar[nextState])
            {
                costSoFar[nextState] = newCost;
                int priority = newCost + misplacedTilesHeuristic(nextState);
                pq.push({priority, nextState});
                front++;
            }
        }
    }

    return -1;
}

int aStarSearch2(const string &initialState)
{
    int front = 0;
    priority_queue<pair<int, string>, vector<pair<int, string>>, greater<pair<int, string>>> pq;
    unordered_map<string, int> costSoFar;

    pq.push({sumDistanceTiles(initialState), initialState});
    costSoFar[initialState] = 0;

    while (!pq.empty())
    {
        string currentState = pq.top().second;
        int currentCost = costSoFar[currentState] + sumDistanceTiles(currentState);
        pq.pop();

        if (isGoalState(currentState))
        {
            return front;
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto &nextState : nextStates)
        {
            int newCost = costSoFar[currentState] + 1;
            if (costSoFar.find(nextState) == costSoFar.end() || newCost < costSoFar[nextState])
            {
                costSoFar[nextState] = newCost;
                int priority = newCost + sumDistanceTiles(nextState);
                pq.push({priority, nextState});
                front++;
            }
        }
    }

    return -1;
}

int main()
{
    // Open the input file stream to read initial states
    // ifstream inFile("puzzles.txt");
    // if (!inFile.is_open()) {
    //     cout << "Unable to open input file." << endl;
    //     return 1;
    // }

    // // Open the output file stream for writing answers
    // ofstream outFile("output.txt");
    // if (!outFile.is_open()) {
    //     cout << "Unable to open output file." << endl;
    //     inFile.close(); // Close the input file stream
    //     return 1;
    // }

    // // Write the table header to the output file
    // outFile << "Initial State\tSolution\tb\tA1\tA2\n";

    // string initialState;
    // // Read each initial state from the input file
    // while (getline(inFile, initialState))
    // {
        string initialState;
        cin>>initialState;
        int solution = aStarSearch(initialState);
        // int b = bfs(initialState);
        int a1 = aStarSearch1(initialState);
        int a2 = aStarSearch2(initialState);

        // Write the values for each state to the output file
        // outFile << initialState << "\t" << solution << "\t" << b << "\t" << a1 << "\t" << a2 << "\n";

        cout << solution<<" "<<a1<<" "<<a2;
        // if (inFile.fail()) {
        //     cout << "Error reading input file." << endl;
        //     break;
        // }
    // }

    // Close the file streams
    // inFile.close();
    // outFile.close();

    // cout << "Answers written to output.txt successfully." << endl;

    return 0;
}
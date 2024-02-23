#include <iostream>
#include <queue>
#include <unordered_map>
#include <string>
#include <vector>
#include <cmath>
using namespace std;


bool isGoalState(const string& state) {
    return state == "ABCDEFGHIJKLMNO#";
}


// int misplacedTilesHeuristic(const string& state) {
//     int count = 0;
//     for (int i = 0; i < state.size(); ++i) {
//         if (state[i] != '#' && state[i] != "ABCDEFGHIJKLMNO"[i]) {
//             ++count;
//         }
//     }
//     return count;
// }

int sumDistanceTiles(const string& state){
int distance = 0;
    for (int i = 0; i < state.size(); ++i) {
        if (state[i] != '#') {
            int correctX = (state[i] - 'A') / 4;
            int correctY = (state[i] - 'A') % 4;
            int currentX = i / 4;
            int currentY = i % 4;
            distance += abs(correctX - currentX) + abs(correctY - currentY);
        }
    }
    return distance;
}


vector<string> generateNextStates(const string& state) {
    vector<string> nextStates;
    int emptyIndex = state.find('#');

    
    int dx[] = {-1, 1, 0, 0};
    int dy[] = {0, 0, -1, 1};
    string directions = "UDLR";

    for (int i = 0; i < 4; ++i) {
        int newX = emptyIndex / 4 + dx[i];
        int newY = emptyIndex % 4 + dy[i];
        if (newX >= 0 && newX < 4 && newY >= 0 && newY < 4) {
            string nextState = state;
            swap(nextState[emptyIndex], nextState[newX * 4 + newY]);
            nextStates.push_back(nextState);
        }
    }
    return nextStates;
}


int aStarSearch(const string& initialState) {
    priority_queue<pair<int, string>, vector<pair<int, string>>, greater<pair<int, string>>> pq;
    unordered_map<string, int> costSoFar;

    pq.push({sumDistanceTiles(initialState), initialState});
    costSoFar[initialState] = 0;

    while (!pq.empty()) {
        string currentState = pq.top().second;
        int currentCost = costSoFar[currentState] + sumDistanceTiles(currentState);
        pq.pop();

        if (isGoalState(currentState)) {
            return costSoFar[currentState];
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto& nextState : nextStates) {
            int newCost = costSoFar[currentState] + 1;
            if (costSoFar.find(nextState) == costSoFar.end() || newCost < costSoFar[nextState]) {
                costSoFar[nextState] = newCost;
                int priority = newCost + sumDistanceTiles(nextState);
                pq.push({priority, nextState});
            }
        }
    }

    return -1;
}

int main() {
    string initialState;
    cin >> initialState;

    int shortestPathCost = aStarSearch(initialState);
    cout << shortestPathCost << endl;

    return 0;
}

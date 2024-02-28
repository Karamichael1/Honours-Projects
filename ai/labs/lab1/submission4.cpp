#include <iostream>
#include <queue>
#include <unordered_set>
#include <string>
using namespace std;


bool isGoalState(const string& state) {
    return state == "ABCDEFGHIJKLMNO#";
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
int bfs(const string& initialState) {
    queue<pair<string, int>> q;
    unordered_set<string> visited;

    q.push({initialState, 0});
    visited.insert(initialState);

    while (!q.empty()) {
        string currentState = q.front().first;
        int cost = q.front().second;
        q.pop();

        if (isGoalState(currentState)) {
            return cost;
        }

        vector<string> nextStates = generateNextStates(currentState);
        for (const auto& nextState : nextStates) {
            if (visited.find(nextState) == visited.end()) {
                q.push({nextState, cost + 1});
                visited.insert(nextState);
            }
        }
    }

    return -1;
}

int main() {
    string initialState;
    cin >> initialState;

    int shortestPathCost = bfs(initialState);
    cout << shortestPathCost << endl;

    return 0;
}

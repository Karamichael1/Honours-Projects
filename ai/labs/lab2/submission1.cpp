#include <iostream>
#include <vector>
#include <utility>
#include <limits>

using namespace std;

typedef pair<int, int> Point;

Point readPoint() {
    int x, y;
    char comma;
    cin >> x >> comma >> y;
    return make_pair(x, y);
}

Point findNashEquilibrium(const vector<vector<Point>>& matrix) {
    int matrixSize = matrix.size();

    vector<int> maxValues(matrixSize, numeric_limits<int>::min());
    for (int i = 0; i < matrixSize; ++i) {
        for (int j = 0; j < matrixSize; ++j) {
            maxValues[i] = max(maxValues[i], matrix[i][j].first);
        }
    }

    int maxRowIndex = 0;
    for (int i = 1; i < matrixSize; ++i) {
        if (maxValues[i] > maxValues[maxRowIndex]) {
            maxRowIndex = i;
        }
    }

    int maxColIndex = 0;
    for (int j = 1; j < matrixSize; ++j) {
        if (matrix[maxRowIndex][j].second > matrix[maxRowIndex][maxColIndex].second) {
            maxColIndex = j;
        }
    }

    return matrix[maxRowIndex][maxColIndex];
}

int main() {
    int matrixSize;
    cin >> matrixSize;

    vector<vector<Point>> matrix(matrixSize, vector<Point>(matrixSize));

    for (int i = 0; i < matrixSize; ++i) {
        for (int j = 0; j < matrixSize; ++j) {
            matrix[i][j] = readPoint();
        }
    }

    Point nashEquilibrium = findNashEquilibrium(matrix);

    cout << nashEquilibrium.first << "," << nashEquilibrium.second << endl;

    return 0;
}

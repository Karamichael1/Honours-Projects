import numpy as np
import math as m


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def forwardProp(weights, biases, input):
    mid = input
    for w, b in zip(weights, biases):
        pre = np.dot(mid, w) + b
        mid = sigmoid(pre)
    return mid


W1 = np.array([[2, 1, -1], [-2, -4, 1]])

W2 = np.array([[-2, 3], [3, -1], [5, 0]])

biases = [np.array([1, -1, 2]), np.array([0, -1])]

input_data = np.array([[2, 1]])

result = forwardProp([W1, W2], biases, input_data)
print(result)

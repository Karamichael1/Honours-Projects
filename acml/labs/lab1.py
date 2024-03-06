import numpy as np

class Perceptron(object):
    def __init__(self, lrate=0.01, epochs=10):
        self.lrate = lrate
        self.epochs = epochs
        self.activation_func = self._unit_step_func
        self.bias = None
        self.weights = None

    def fit(self, X, T):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        for epoch in range(self.epochs):
            I = np.random.permutation(n_samples)  # Randomly shuffle indices
            for i in I:
                x_i = X[i]
                target = T[i]
                linear_output = np.dot(x_i, self.weights) + self.bias
                y_predicted = self.activation_func(linear_output)
                update = self.lrate * (target - y_predicted)
                self.weights += update * x_i
                self.bias += update

            loss = self._compute_loss(X, T)
            print(f"Epoch {epoch + 1}, Loss: {loss}")

    def predict(self, X):
        linear_output = np.dot(X, self.weights) + self.bias
        y_predicted = self.activation_func(linear_output)
        return y_predicted

    def _unit_step_func(self, x):
        return np.where(x >= 0, 1, 0)

    def _compute_loss(self, X, T):
        y_predicted = self.predict(X)
        return np.mean(np.abs(T - y_predicted))

# Test dataset
X = np.array([[0, 0],
              [0, 1],
              [1, 0],
              [1, 1]])

T = np.array([1, 1, 1, 0])

# Create and train perceptron
perceptron = Perceptron(lrate=0.01, epochs=10)
perceptron.fit(X, T)

# Plot linear discriminant
import matplotlib.pyplot as plt

plt.scatter(X[:, 0], X[:, 1], c=T)
plt.xlabel('x1')
plt.ylabel('x2')

# Plot the decision boundary
x1_values = np.linspace(0, 1.5, 100)
x2_values = (-perceptron.weights[0] * x1_values - perceptron.bias) / perceptron.weights[1]
plt.plot(x1_values, x2_values, color='r')

plt.show()

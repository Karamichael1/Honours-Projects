import numpy as np
import matplotlib.pyplot as plt

X = np.array([[0, 0], [1, 1], [1, 0], [1, 1]])
T = np.array([0, 1, 1, 0])

# Perceptron Training Algorithm
def perceptron_train(X, T, epochs):
    N, m = X.shape
    w = np.zeros(m)  # Initialize weights
    b = 0  # Initialize bias
    losses = []  # List to store losses after each epoch
    for epoch in range(epochs):
        I = np.random.permutation(N)  # Shuffle indices
        for i in I:
            y_pred = np.dot(X[i], w) + b
            if y_pred >= 0:
                y_pred = 1
            else:
                y_pred = 0
            error = T[i] - y_pred
            w += error * X[i]  # Update weights
            b += error  # Update bias
        loss = compute_loss(X, T, w, b)  # Compute loss after each epoch
        losses.append(loss)
        print(f"Epoch {epoch+1}, Loss: {loss:.4f}")
    return w, b, losses

# Loss function
def compute_loss(X, T, w, b):
    N = len(T)
    loss = 0
    for i in range(N):
        y_pred = np.dot(X[i], w) + b
        if y_pred >= 0:
            y_pred = 1
        else:
            y_pred = 0
        if y_pred != T[i]:
            loss += 1
    return loss / N

# Plot the dataset and linear discriminant
def plot_dataset_and_discriminant(X, T, w, b):
    plt.scatter(X[:, 0], X[:, 1], c=T)
    x_vals = np.linspace(0, 1, 100)
    y_vals = (-w[0] * x_vals - b) / w[1]
    plt.plot(x_vals, y_vals, '-r')
    plt.xlabel('x1')
    plt.ylabel('x2')
    plt.title('Linear Discriminant')
    plt.show()

# Train the perceptron
epochs = 100
w, b, losses = perceptron_train(X, T, epochs)
print("Weights:", w)
print("Bias:", b)

# Visualize the linear discriminant
plot_dataset_and_discriminant(X, T, w, b)

# Plot the loss curve
plt.plot(range(1, epochs+1), losses)
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.title('Loss Curve')
plt.show()

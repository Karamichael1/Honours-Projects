import numpy as np
from sklearn import datasets
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

iris = datasets.load_iris()
X = iris.data
y = iris.target


enc = OneHotEncoder(handle_unknown='ignore')
y_onehot = enc.fit_transform(y.reshape(-1, 1)).toarray()


X_train, X_test, y_train, y_test = train_test_split(X, y_onehot, test_size=0.2, random_state=42)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def forward_prop(X, W1, W2, b1, b2):
    z1 = np.dot(X, W1) + b1
    a1 = sigmoid(z1)
    z2 = np.dot(a1, W2) + b2
    a2 = sigmoid(z2)
    return a1, a2


def backprop(X, y, W1, W2, b1, b2, learning_rate=0.1):
    m = X.shape[0]
    a1, a2 = forward_prop(X, W1, W2, b1, b2)
    
    dz2 = a2 - y
    dW2 = np.dot(a1.T, dz2) / m
    db2 = np.sum(dz2, axis=0) / m
    
    dz1 = np.dot(dz2, W2.T) * a1 * (1 - a1)
    dW1 = np.dot(X.T, dz1) / m
    db1 = np.sum(dz1, axis=0) / m
    
    W2 -= learning_rate * dW2
    b2 -= learning_rate * db2
    W1 -= learning_rate * dW1
    b1 -= learning_rate * db1
    
    return W1, W2, b1, b2


np.random.seed(42)
n_x = X_train.shape[1]
n_h = 4  # Number of hidden units
n_y = y_train.shape[1]

W1 = np.random.randn(n_x, n_h)
b1 = np.zeros((1, n_h))
W2 = np.random.randn(n_h, n_y)
b2 = np.zeros((1, n_y))


epochs = 10000
for epoch in range(epochs):
    
    indices = np.random.permutation(X_train.shape[0])
    X_train = X_train[indices]
    y_train = y_train[indices]
    
  
    W1, W2, b1, b2 = backprop(X_train, y_train, W1, W2, b1, b2)
    
   
    a1, a2 = forward_prop(X_train, W1, W2, b1, b2)
    error = np.mean(np.abs(a2 - y_train)**2)
    print(f"Epoch {epoch+1}/{epochs}, Error: {error:.4f}")


a1, a2 = forward_prop(X_test, W1, W2, b1, b2)
predictions = np.argmax(a2, axis=1)
targets = np.argmax(y_test, axis=1)
accuracy = np.mean(predictions == targets)
print(f"Test accuracy: {accuracy:.4f}")
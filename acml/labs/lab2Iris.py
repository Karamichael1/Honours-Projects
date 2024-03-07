import numpy as np
from sklearn.datasets import load_iris
from sklearn.preprocessing import OneHotEncoder

# Load Iris dataset
iris_data = load_iris()
X = iris_data.data  # Features
T = iris_data.target  # Target

# Convert target dataset to one-hot encoding
one_hot_encoder = OneHotEncoder(categories='auto')
T_one_hot = one_hot_encoder.fit_transform(T.reshape(-1, 1))

print("Original target dataset (first 5 samples):\n", T[:5])
print("One-hot encoded target dataset (first 5 samples):\n", T_one_hot[:5])

import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def forward_propagation(input_data, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output):
    weighted_sum_hidden = np.dot(input_data, weights_input_hidden) + biases_hidden
    activations_hidden = sigmoid(weighted_sum_hidden)
    weighted_sum_output = np.dot(activations_hidden, weights_hidden_output) + biases_output
    activations_output = sigmoid(weighted_sum_output)
    return activations_hidden, activations_output


def sum_squared_loss(output, target):
    return 0.5 * np.sum((output - target) ** 2)


def backpropagation(input_data, target_output, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output, learning_rate=0.1):
    num_samples = input_data.shape[0]
    activations_hidden, activations_output = forward_propagation(input_data, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output)
    
    error_output = activations_output - target_output
    gradient_weights_hidden_output = np.dot(activations_hidden.T, error_output) / num_samples
    gradient_biases_output = np.sum(error_output, axis=0) / num_samples
    
    error_hidden = np.dot(error_output, weights_hidden_output.T) * activations_hidden * (1 - activations_hidden)
    gradient_weights_input_hidden = np.dot(input_data.T, error_hidden) / num_samples
    gradient_biases_hidden = np.sum(error_hidden, axis=0) / num_samples
    
    weights_hidden_output -= learning_rate * gradient_weights_hidden_output
    biases_output -= learning_rate * gradient_biases_output
    weights_input_hidden -= learning_rate * gradient_weights_input_hidden
    biases_hidden -= learning_rate * gradient_biases_hidden
    
    return weights_input_hidden, weights_hidden_output, biases_hidden, biases_output


input_values = []
for _ in range(7):
    input_values.append(float(input()))

input_data = np.array(input_values[:4]).reshape(1, 4)
target_output = np.array(input_values[4:])


weights_input_hidden = np.ones((4, 8))
biases_hidden = np.ones((1, 8))
weights_hidden_output = np.ones((8, 3))
biases_output = np.ones((1, 3))

_, activations_output = forward_propagation(input_data, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output)
loss_before_training = sum_squared_loss(activations_output, target_output)


weights_input_hidden, weights_hidden_output, biases_hidden, biases_output = backpropagation(input_data, target_output, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output)

_, activations_output = forward_propagation(input_data, weights_input_hidden, weights_hidden_output, biases_hidden, biases_output)
loss_after_training = sum_squared_loss(activations_output, target_output)

print(f"{loss_before_training:.4f}")
print(f"{loss_after_training:.4f}")
import matplotlib.pyplot as plt
import numpy as np

# Data from the table
data = {
    'Solution': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 12, 14, 14, 16, 16, 16, 16, 16, 20, 22],
    'bfs': [11, 23, 22, 11, 33, 22, 23, 22, 11, 33, 109, 109, 83, 83, 59, 83, 92, 83, 88, 107, 1529, 1728,1213,1593,1546,1792, 1822, 1801, 2252, 1279, 1838, 23195, 112286, 121375, 348498, 1000000, 1000000, 1000000, 1000000, 1000000, 1000000],
    'A1': [5, 6, 5, 5, 6, 5, 6, 5, 5, 6, 8, 8, 10, 11, 9, 11, 11, 10, 8, 10, 17, 19, 15, 32, 39, 28, 21, 25, 29, 17, 34, 77, 580, 181, 90, 77, 222, 442, 285, 1057, 13854],
    'A2': [5, 6, 5, 5, 6, 5, 6, 5, 5, 6, 8, 8, 10, 9, 9, 11, 10, 8, 8, 10, 17, 19, 15, 16, 21, 20, 21, 19, 19, 17, 23, 35, 158, 36, 51, 29, 34, 299, 34, 194, 1461]
}

# Calculate the average number of nodes expanded for each solution length
averages = {}
for algorithm in ['bfs', 'A1', 'A2']:
    averages[algorithm] = {}
    for solution_length in set(data['Solution']):
        indices = [i for i in range(len(data['Solution'])) if data['Solution'][i] == solution_length]
        avg_nodes = np.mean([data[algorithm][i] for i in indices])
        averages[algorithm][solution_length] = avg_nodes

# Plot the graph
for algorithm, color in zip(['bfs', 'A1', 'A2'], ['r', 'g', 'b']):
    plt.plot(list(averages[algorithm].keys()), list(averages[algorithm].values()), label=algorithm, color=color, marker='o')

plt.xlabel('Solution Length')
plt.ylabel('Average Nodes Expanded (log scale)')
plt.yscale('log')
plt.title('Nodes Expanded vs Solution Length')
plt.legend()
plt.grid(True)
plt.show()
solution_length = len(data['Solution'])

# Calculate the average number of nodes expanded for each solution length
# averages = {}
# for algorithm in ['bfs', 'A1', 'A2']:
#     averages[algorithm] = {}
#     for solution_length in set(data['Solution']):
#         indices = [i for i in range(len(data['Solution'])) if data['Solution'][i] == solution_length]
#         avg_nodes = np.mean([data[algorithm][i] for i in indices])
#         averages[algorithm][solution_length] = avg_nodes

# # Plot the graph
# for algorithm, color in zip(['bfs', 'A1', 'A2'], ['r', 'g', 'b']):
#     plt.plot(list(averages[algorithm].keys()), list(averages[algorithm].values()), label=algorithm, color=color, marker='o')

# plt.xlabel('Solution Length')
# plt.ylabel('Average Nodes Expanded (log scale)')
# plt.yscale('log')
# plt.title('Nodes Expanded vs Solution Length')
# plt.legend()
# plt.grid(True)
# plt.show()
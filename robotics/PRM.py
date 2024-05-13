import math
import random
import matplotlib.pyplot as plt

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)

def manhattan_distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def is_inside_obstacle(point, obstacles):
    for obstacle in obstacles:
        if (
            obstacle[0][0] <= point.x <= obstacle[1][0]
            and obstacle[0][1] <= point.y <= obstacle[1][1]
        ):
            return True
    return False

def is_collision_free(node1, node2, obstacles):
    for obstacle in obstacles:
        if (
            min(node1.x, node2.x) <= obstacle[1][0]
            and max(node1.x, node2.x) >= obstacle[0][0]
            and min(node1.y, node2.y) <= obstacle[1][1]
            and max(node1.y, node2.y) >= obstacle[0][1]
        ):
            return False
    return True

def find_path(start_point, target_point, obstacles, num_samples=1500, neighbor_radius=40):
    roadmap = []

    # Generate random samples
    while len(roadmap) < num_samples:
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        new_point = Node(x, y)
        if not is_inside_obstacle(new_point, obstacles):
            roadmap.append(new_point)

    # Add start and target nodes to the roadmap
    start_node = Node(start_point[0], start_point[1])
    target_node = Node(target_point[0], target_point[1])
    roadmap.append(start_node)
    roadmap.append(target_node)

    # Connect neighboring nodes
    for i in range(len(roadmap)):
        for j in range(i + 1, len(roadmap)):
            node1 = roadmap[i]
            node2 = roadmap[j]
            if distance(node1, node2) <= neighbor_radius and is_collision_free(node1, node2, obstacles):
                node1.neighbors.append(node2)
                node2.neighbors.append(node1)

    # Find the shortest path using A* algorithm
    open_set = [start_node]
    closed_set = []

    while open_set:
        current_node = min(open_set, key=lambda node: node.f)

        if current_node == target_node:
            path = []
            while current_node:
                path.append((current_node.x, current_node.y))
                current_node = current_node.parent
            path.reverse()
            return path

        open_set.remove(current_node)
        closed_set.append(current_node)

        for neighbor in current_node.neighbors:
            if neighbor in closed_set:
                continue

            tentative_g = current_node.g + distance(current_node, neighbor)

            if neighbor not in open_set:
                open_set.append(neighbor)
            elif tentative_g >= neighbor.g:
                continue

            neighbor.parent = current_node
            neighbor.g = tentative_g
            neighbor.h = manhattan_distance(neighbor, target_node)
            neighbor.f = neighbor.g + neighbor.h

    return None

# Get user input
start_str, target_str = input().split(";")
start_point = tuple(map(int, start_str.split(",")))
target_point = tuple(map(int, target_str.split(",")))

obstacles = []
while True:
    obstacle_str = input()
    if obstacle_str == "-1":
        break
    obstacle_coords = obstacle_str.split(";")
    top_left = tuple(map(int, obstacle_coords[0].split(",")))
    bottom_right = tuple(map(int, obstacle_coords[1].split(",")))
    obstacles.append((top_left, bottom_right))

# Find the path
path = find_path(start_point, target_point, obstacles)

# Create a plot
fig, ax = plt.subplots()

# Plot obstacles
for obstacle in obstacles:
    obstacle_x = [obstacle[0][0], obstacle[1][0], obstacle[1][0], obstacle[0][0], obstacle[0][0]]
    obstacle_y = [obstacle[0][1], obstacle[0][1], obstacle[1][1], obstacle[1][1], obstacle[0][1]]
    ax.plot(obstacle_x, obstacle_y, 'r-')

# Plot start and target points
ax.plot(start_point[0], start_point[1], 'go', label='Start')
ax.plot(target_point[0], target_point[1], 'ro', label='Target')

# Plot the path
if path:
    path_x = [waypoint[0] for waypoint in path]
    path_y = [waypoint[1] for waypoint in path]
    ax.plot(path_x, path_y, 'b-', label='Path')

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('PRM Path')

# Add legend
ax.legend()

# Display the plot
plt.show()

for waypoint in path:
    print(waypoint[0], waypoint[1])
import math
import random
import matplotlib.pyplot as plt
import numpy as np

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

def get_map(pgm_file_path):
    with open(pgm_file_path, 'rb') as file:
        # Read the header
        magic = file.readline().strip()
        if magic != b'P5':
            raise ValueError('Invalid PGM file format')
        
        # Skip the comment line
        file.readline()
        
        # Read the image dimensions
        dimensions = file.readline().split()
        width = int(dimensions[0])
        height = int(dimensions[1])
        
        # Read the maximum pixel value
        max_value = int(file.readline())
        
        # Read the pixel data
        pixel_data = np.fromfile(file, dtype=np.uint8)
        
        # Reshape the pixel data into a 2D array
        image_array = pixel_data.reshape((height, width))
        
        return image_array, width, height, max_value
    
def get_obstacles(image_array):
    obstacles = []
    height, width = image_array.shape
    
    current_obstacle = None
    for y in range(height):
        for x in range(width):
            if image_array[y, x] == 0:  # Black pixel, obstacle
                if current_obstacle is None:
                    current_obstacle = (x, y, x, y)
                else:
                    current_obstacle = (min(current_obstacle[0], x), min(current_obstacle[1], y),
                                        max(current_obstacle[2], x), max(current_obstacle[3], y))
            else:  # White pixel, free space
                if current_obstacle is not None:
                    top_left = (current_obstacle[0], current_obstacle[1])
                    bottom_right = (current_obstacle[2] + 1, current_obstacle[3] + 1)
                    obstacles.append((top_left, bottom_right))
                    current_obstacle = None
    
    if current_obstacle is not None:
        top_left = (current_obstacle[0], current_obstacle[1])
        bottom_right = (current_obstacle[2] + 1, current_obstacle[3] + 1)
        obstacles.append((top_left, bottom_right))
    
    return obstacles

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

def plot_map(obstacles, height, width, path, start_point, target_point):
    fig, ax = plt.subplots()

    # Plot obstacles
    for obstacle in obstacles:
        obstacle_x = [obstacle[0][0], obstacle[1][0], obstacle[1][0], obstacle[0][0], obstacle[0][0]]
        obstacle_y = [obstacle[0][1], obstacle[0][1], obstacle[1][1], obstacle[1][1], obstacle[0][1]]
        ax.plot(obstacle_x, obstacle_y, 'k-')

    # Plot start and target points
    ax.plot(start_point[0], start_point[1], 'go', markersize=10)
    ax.plot(target_point[0], target_point[1], 'ro', markersize=10)

    # Plot path
    if path is not None:
        path_x, path_y = zip(*path)
        ax.plot(path_x, path_y, 'b-', linewidth=2)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_title('Path Planning')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.show()

# Get user input
start_str, target_str = input().split(";")
start_point = tuple(map(int, start_str.split(",")))
target_point = tuple(map(int, target_str.split(",")))

# Read the PGM map
image_array, width, height, max_value = get_map('C:\\Users\\karam\\OneDrive\\Documents\\GitHub\\Honours-Projects\\robotics\\map1.pgm')

# Get obstacles from the map
obstacles = get_obstacles(image_array)

# Find the path
path = find_path(start_point, target_point, obstacles)

# Print the path
if path is not None:
    print("Path:")
    for waypoint in path:
        print(f"({waypoint[0]}, {waypoint[1]})")
else:
    print("No path found.")

# Plot the map with path, start, and target points
plot_map(obstacles, height, width, path, start_point, target_point)
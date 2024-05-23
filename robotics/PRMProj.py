import math
import random
import matplotlib.pyplot as plt
import numpy as np

DENSITY = 1500
NEIGHBOR_RADIUS = 60

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

    def __eq__(self, other):
        if self.x == other.x and self.y == other.y:
            return True
        return False

    def __repr__(self):
        return f"({self.x},{self.y})"

def get_map(pgm_file_path):
    with open(pgm_file_path, 'rb') as file:
        # Read the magic number
        magic = file.readline().strip()
        if magic != b'P5':
            raise ValueError('Invalid PGM file format')

        # Skip the comment line
        # file.readline()

        # Read the image dimensions
        dimensions = file.readline().split()
        width = int(dimensions[0])
        height = int(dimensions[1])

        # Read the maximum pixel value
        max_value = int(file.readline())

        # Read the pixel data line by line
        pixel_data = bytearray()
        for _ in range(height):
            pixel_data.extend(file.read(width))

        # Convert the pixel data to a NumPy array
        image_array = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width))

        return image_array, width, height, max_value
    
def is_obst(x, y): return True if image_array[y, x] < 180 else False
    
def get_obstacles(image_array):
    obstacles = set()
    height, width = image_array.shape
    
    # current_obstacle = None
    # for y in range(height):
    #     for x in range(width):
    #         if image_array[y, x] != 0:  # Black pixel, obstacle
    #             if current_obstacle is None:
    #                 current_obstacle = (x, y, x, y)
    #             else:
    #                 current_obstacle = (min(current_obstacle[0], x), min(current_obstacle[1], y),
    #                                     max(current_obstacle[2], x), max(current_obstacle[3], y))
    #         else:  # White pixel, free space
    #             if current_obstacle is not None:
    #                 top_left = (current_obstacle[0], current_obstacle[1])
    #                 bottom_right = (current_obstacle[2] + 1, current_obstacle[3] + 1)
    #                 obstacles.append((top_left, bottom_right))
    #                 current_obstacle = None
    
    # if current_obstacle is not None:
    #     top_left = (current_obstacle[0], current_obstacle[1])
    #     bottom_right = (current_obstacle[2] + 1, current_obstacle[3] + 1)
    #     obstacles.append((top_left, bottom_right))

    for y in range(height):
        for x in range(width):
            if is_obst(x, y):  # Black pixel, obstacle
                obstacles.add((x,y))

    to_add = set()
    for x,y in obstacles:
        to_add.add((x-1, y))
        to_add.add((x, y-1))
        to_add.add((x+1, y))
        to_add.add((x, y+1))

    for i in to_add:
        obstacles.add(i)
    
    return obstacles

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)

def manhattan_distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def is_inside_obstacle(point, obstacles):
    # for obstacle in obstacles:
    #     if (
    #         obstacle[0][0] <= point.x <= obstacle[1][0]
    #         and obstacle[0][1] <= point.y <= obstacle[1][1]
    #     ):
    #         return True
    # return False

    for x,y in obstacles:
        # print(obs, point)
        if point.x == x and point.y == y:
            return True
    
    return False

    return True if point in obstacles else False

# Bresenham's line algorithm implementation from GeeksforGeeks
def bresenham(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    line_points = []

    while True:
        line_points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    return line_points

def is_collision_free(node1, node2, obstacles, obstacle_clearance=0):
    line_points = bresenham(node1.x, node1.y, node2.x, node2.y)
    # print(line_points)

    for point in line_points:
        x, y = point
        x = int(x)
        y = int(y)

        # print(x, y)

        # for obstacle in obstacles:
        #     if (
        #         obstacle.x - obstacle_clearance <= x <= obstacle.x + obstacle_clearance
        #         and obstacle.y - obstacle_clearance <= y <= obstacle.y + obstacle_clearance
        #     ):
        #         return False

        # if is_obst(x, y) or is_obst(pad_x, y) or is_obst(x, pad_y) or is_obst(pad_x, pad_y) or is_obst(un_pad_x, y) or is_obst(x, un_pad_y) or is_obst(un_pad_x, un_pad_y):
        #     return False

        # print(x,y)
        if (x, y) in obstacles or (x+1, y) in obstacles or (x,y+1) in obstacles or (x+1, y+1) in obstacles or (x-1,y) in obstacles or (x,y-1) in obstacles or (x-1,y-1) in obstacles:
            return False
    
    # print(line_points)
    return True

# def is_collision_free(node1, node2, obstacles):
#     for obstacle in obstacles:
#         if (
#             min(node1.x, node2.x) <= obstacle[1][0]
#             and max(node1.x, node2.x) >= obstacle[0][0]
#             and min(node1.y, node2.y) <= obstacle[1][1]
#             and max(node1.y, node2.y) >= obstacle[0][1]
#         ):
#             return False
#     return True

roadmap = []
edges = []
def find_path(start_point, target_point, obstacles, image_width, image_height, num_samples=DENSITY, neighbor_radius=NEIGHBOR_RADIUS):
    count = 0
    # Generate random samples within the image bounds
    while len(roadmap) < num_samples:
        x = int(random.uniform(2, image_width-2))
        y = int(random.uniform(2, image_height-2))
        new_point = Node(x, y)
        if not is_inside_obstacle(new_point, obstacles):
            count += 1
            roadmap.append(new_point)

    # Add start and target nodes to the roadmap
    start_node = Node(start_point[0], start_point[1])
    target_node = Node(target_point[0], target_point[1])
    roadmap.append(start_node)
    roadmap.append(target_node)


    # Connect neighboring nodes
    count = 0
    for i in range(len(roadmap)):
        for j in range(i + 1, len(roadmap)):
            node1 = roadmap[i]
            node2 = roadmap[j]
            if distance(node1, node2) <= neighbor_radius and is_collision_free(node1, node2, obstacles, obstacle_clearance=2):
                node1.neighbors.append(node2)
                node2.neighbors.append(node1)
                edges.append((node1,node2))
                
        count += 1
        print(f"Counter: {count} {len(roadmap)}")


    # Find the shortest path using A* algorithm
    open_set = [start_node]
    closed_set = []

    while open_set:
        current_node = min(open_set, key=lambda node: node.f)
        print(current_node.f)

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
    # for obstacle in obstacles:
    #     obstacle_x = [obstacle[0][0], obstacle[1][0], obstacle[1][0], obstacle[0][0], obstacle[0][0]]
    #     obstacle_y = [obstacle[0][1], obstacle[0][1], obstacle[1][1], obstacle[1][1], obstacle[0][1]]
    #     ax.plot(obstacle_x, obstacle_y, 'k-')

    obstacle_x = [x for x,y in obstacles]
    obstacle_y = [y for x,y in obstacles]
    ax.scatter(obstacle_x, obstacle_y, marker="o", s=0.01, color="black")

    # Plot start and target points
    ax.plot(start_point[0], start_point[1], 'o', markersize=10, color="green")
    ax.plot(target_point[0], target_point[1], marker='x', markersize=10, color="blue")

    node_x = [node.x for node in roadmap]
    node_y = [node.y for node in roadmap]
    ax.scatter(node_x, node_y, marker="o", s=1, color="yellow")

    for edge in edges:
        x1, y1 = edge[0].x, edge[0].y
        x2, y2 = edge[1].x, edge[1].y
        ax.plot([x1, x2], [y1, y2], color='purple', linewidth=1)

    # Plot path
    if path is not None:
        path_x, path_y = zip(*path)
        ax.plot(path_x, path_y, 'p-', linewidth=2)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_title('Path Planning')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    plt.savefig('path.png')
    plt.show()

# Get user input
# start_str, target_str = input().split(";")
start_str, target_str = "630,720;1000,700".split(";")
start_point = tuple(map(int, start_str.split(",")))
target_point = tuple(map(int, target_str.split(",")))

# Read the PGM map
image_array, width, height, max_value = get_map('Mapping.pgm')

# Get obstacles from the map
obstacles = get_obstacles(image_array)

fig, ax = plt.subplots()

# Plot obstacles

obstacle_x = [x for x,y in obstacles]
obstacle_y = [y for x,y in obstacles]
ax.scatter(obstacle_x, obstacle_y, marker="o", s=0.01)

ax.set_xlim(0, width)
ax.set_ylim(0, height)
ax.set_aspect('equal')
ax.set_title('Path Planning')
ax.set_xlabel('X')
ax.set_ylabel('Y')
plt.savefig('obstacles.png')
plt.show()

# Find the path
path = find_path(start_point, target_point, obstacles, width, height)

# Print the path
if path is not None:
    print("Path:")
    for waypoint in path:
        print(f"({waypoint[0]}, {waypoint[1]})")
else:
    print("No path found.")

# Plot the map with path, start, and target points
plot_map(obstacles, height, width, path, start_point, target_point)
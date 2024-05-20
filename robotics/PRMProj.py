import math
import random

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.neighbors = []
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None

def read_pgm_map(file_path):
    obstacles = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        height, width = map(int, lines[2].split())
        data = [list(map(int, line.split())) for line in lines[4:]]
        
        current_obstacle = None
        for y in range(height):
            for x in range(width):
                if data[y][x] == 0:  # Black pixel, obstacle
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
    
    return obstacles, height, width

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

def print_map(obstacles, height, width, path, start_point, target_point):
    map = [[' ' for _ in range(width)] for _ in range(height)]

    # Mark obstacles
    for obstacle in obstacles:
        for y in range(obstacle[0][1], obstacle[1][1]):
            for x in range(obstacle[0][0], obstacle[1][0]):
                map[y][x] = '#'

    # Mark start and target points
    map[start_point[1]][start_point[0]] = 'S'
    map[target_point[1]][target_point[0]] = 'T'

    # Mark path
    for waypoint in path:
        map[int(waypoint[1])][int(waypoint[0])] = 'X'

    # Print the map
    for row in map:
        print(''.join(row))

# Get user input
start_str, target_str = input().split(";")
start_point = tuple(map(int, start_str.split(",")))
target_point = tuple(map(int, target_str.split(",")))

obstacles, height, width = read_pgm_map('C:\\Users\\User\\Documents\\GitHub\\Honours-Projects\\robotics\\map1.pgm')

# Find the path
path = find_path(start_point, target_point, obstacles)

# Print the map with path, start, and target points
print_map(obstacles, height, width, path, start_point, target_point)
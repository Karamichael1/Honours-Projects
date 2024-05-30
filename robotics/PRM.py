#!/usr/bin/env python

import math
import random
import numpy as np
import pickle
import sys
import json
import matplotlib.pyplot as plt

DENSITY = 5000
NEIGHBOR_RADIUS = 80

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
        return "({}, {})".format(self.x, self.y)

def get_map(pgm_file_path):
    with open(pgm_file_path, 'rb') as file:
        # Read the magic number
        magic = file.readline().strip()
        if magic != b'P5':
            raise ValueError('Invalid PGM file format')

        # Read the image dimensions
        dimensions = file.readline().split()
        width =  int(round(float(dimensions[0])))
        height =  int(round(float(dimensions[1])))

        # Read the maximum pixel value
        max_value =  int(round(float(file.readline())))

        # Read the pixel data line by line
        pixel_data = bytearray()
        for _ in range(height):
            pixel_data.extend(file.read(width))

        # Convert the pixel data to a NumPy array
        image_array = np.frombuffer(pixel_data, dtype=np.uint8).reshape((height, width))

        return image_array, width, height, max_value

def plot_map(obstacles, height, width, path, start_point, target_point):
    fig, ax = plt.subplots()

    obstacle_x = [x for x,y in obstacles]
    obstacle_y = [y for x,y in obstacles]
    ax.scatter(obstacle_x, obstacle_y, marker="o", s=0.01, color="black")

    # Plot start and target points
    ax.plot(start_point[0], start_point[1], 'o', markersize=10, color="green")
    ax.plot(target_point[0], target_point[1], marker='x', markersize=10, color="blue")

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


def is_obst(x, y, image_array): return True if image_array[y, x] < 180 else False
    
def get_obstacles(image_array):
    obstacles = set()
    height, width = image_array.shape

    for y in range(height):
        for x in range(width):
            if is_obst(x, y, image_array):  # Black pixel, obstacle
                obstacles.add((x,y))

    to_add = set()
    padding = 9
    for x, y in obstacles:
        for dx in range(-padding, padding+1):
            for dy in range(-padding, padding+1):
                to_add.add((x + dx, y + dy))

    for i in to_add:
        obstacles.add(i)
    
    return obstacles

def distance(node1, node2):
    return math.sqrt((node1.x - node2.x) ** 2 + (node1.y - node2.y) ** 2)

def manhattan_distance(node1, node2):
    return abs(node1.x - node2.x) + abs(node1.y - node2.y)

def is_inside_obstacle(point, obstacles):
    for x,y in obstacles:
        if point.x == x and point.y == y:
            return True
    
    return False

# Bresenham's line algorithm implementation from GeeksforGeeks
def bresenham(x1, y1, x2, y2):
    x1, y1, x2, y2 =  int(round(x1)),  int(round(y1)),  int(round(x2)),  int(round(y2))
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

    for point in line_points:
        x, y = point
        x =  int(round(x))
        y =  int(round(y))

        if (x, y) in obstacles or (x+1, y) in obstacles or (x,y+1) in obstacles or (x+1, y+1) in obstacles or (x-1,y) in obstacles or (x,y-1) in obstacles or (x-1,y-1) in obstacles:
            return False
    
    return True

def find_path(start_point, target_point, map_path, save_path, neighbor_radius=NEIGHBOR_RADIUS):
    print('Loading roadmap...')
    roadmap = load_roadmap(save_path)
    roadmap = [Node(point[0], point[1]) for point in roadmap]
    edges = []

    image_array, image_width, image_height, max_value = get_map(map_path)
    # Get obstacles from the map
    obstacles = get_obstacles(image_array)

    print('Planning path...')
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

            plot_map(obstacles, image_height, image_width, path, start_point, target_point)

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

def build_roadmap(map_path, save_path, num_samples=DENSITY, neighbor_radius=NEIGHBOR_RADIUS):
    print('Building Roadmap...')
    roadmap = []
    image_array, image_width, image_height, max_value = get_map(map_path)

    # Get obstacles from the map
    obstacles = get_obstacles(image_array)
    count = 0
    # Generate random samples within the image bounds
    while len(roadmap) < num_samples:
        x =  int(round(random.uniform(2, image_width-2)))
        y =  int(round(random.uniform(2, image_height-2)))
        new_point = Node(x, y)
        if not is_inside_obstacle(new_point, obstacles):
            count += 1
            roadmap.append([new_point.x, new_point.y])

    # save roadmap, edges
    with open(save_path, 'wb') as file:
        pickle.dump((roadmap), file)

    print('Roadmap saved to', save_path)

def load_roadmap(save_path):
    with open(save_path, 'rb') as file:
        roadmap = pickle.load(file)
    return roadmap

def get_path_args():
    if len(sys.argv) != 3:
        print("Usage: python script.py map_path save_path")
        return None
    try:
        map_path = sys.argv[1]
        save_path = sys.argv[2]
        return map_path, save_path
    except ValueError:
        print("Coordinates must be numeric")
        return None
    
if __name__ == '__main__':
    map_path, save_path = get_path_args()
    build_roadmap(map_path, save_path)

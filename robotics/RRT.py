import numpy as np
import matplotlib.pyplot as plt

class RRT:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.tree = [start]
        
    def random_point(self):
        return np.random.randint(0, 100, 2)
    
    def nearest_node(self, point):
        distances = [np.linalg.norm(np.array(node) - np.array(point)) for node in self.tree]
        return self.tree[np.argmin(distances)]
    
    def new_node(self, near_node, point, step_size=5):
        direction = (np.array(point) - np.array(near_node)) / (np.linalg.norm(np.array(point) - np.array(near_node)) + 1e-8)
        new_node = near_node + step_size * direction
        return tuple(np.round(new_node).astype(int))
    
    def check_collision(self, node1, node2):
        for obs in self.obstacles:
            if self.line_intersection(node1, node2, obs[:2], obs[2:]):
                return True
        return False
    
    def line_intersection(self, p1, p2, q1, q2):
        def ccw(A, B, C):
            return np.int64(C[1] - A[1]) * np.int64(B[0] - A[0]) > np.int64(B[1] - A[1]) * np.int64(C[0] - A[0])
        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    
    def build_rrt(self, max_iter=1000):
        for _ in range(max_iter):
            rand_point = self.random_point()
            near_node = self.nearest_node(rand_point)
            new_node = self.new_node(near_node, rand_point)
            if not self.check_collision(near_node, new_node):
                self.tree.append(new_node)
                if np.linalg.norm(np.array(new_node) - np.array(self.goal)) < 5:
                    self.tree.append(self.goal)
                    return self.get_path()
        return None
    
    def get_path(self):
        path = [self.goal]
        while path[-1] != self.start:
            current_node = path[-1]
            distances = [np.linalg.norm(np.array(node) - np.array(current_node)) for node in self.tree]
            nearest_node = self.tree[np.argmin(distances)]
            path.append(nearest_node)
        return path[::-1]

# User input
print("Enter the starting point coordinates (x,y):")
start_input = input().split(',')
start = tuple(map(int, start_input))

print("Enter the target point coordinates (x,y):")
goal_input = input().split(',')
goal = tuple(map(int, goal_input))

print("Enter the obstacle coordinates in the format 'x1,y1;x2,y2;...':")
obstacle_input = input().split(';')
obstacles = [tuple(map(int, obs.split(','))) for obs in obstacle_input]

# Create RRT object and find path
rrt = RRT(start, goal, obstacles)
path = rrt.build_rrt()

# Output path
if path:
    print("Path found:")
    print(' '.join([f"{point[0]},{point[1]}" for point in path]))
else:
    print("No path found.")
import numpy as np
import matplotlib.pyplot as plt

class PRM:
    def __init__(self, start, goal, obstacles):
        self.start = start
        self.goal = goal
        self.obstacles = obstacles
        self.graph = []
        
    def random_point(self):
        return np.random.randint(0, 100, 2)
    
    def check_collision(self, node1, node2):
        for obs in self.obstacles:
            if self.line_intersection(node1, node2, obs[:2], obs[2:]):
                return True
        return False
    
    def line_intersection(self, p1, p2, q1, q2):
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)
    
    def build_roadmap(self, num_nodes=100, k=10):
        self.graph.append(self.start)
        self.graph.append(self.goal)
        while len(self.graph) < num_nodes:
            rand_point = self.random_point()
            if not any(self.check_collision(rand_point, obs[:2]) for obs in self.obstacles):
                self.graph.append(tuple(rand_point))
        for i in range(len(self.graph)):
            distances = [np.linalg.norm(np.array(self.graph[i]) - np.array(node)) for node in self.graph]
            nearest_indices = np.argsort(distances)[1:k+1]
            for j in nearest_indices:
                if not self.check_collision(self.graph[i], self.graph[j]):
                    self.graph[i] = (self.graph[i], self.graph[j])
                    self.graph[j] = (self.graph[j], self.graph[i])
                    
    def get_path(self):
        visited = set()
        queue = [(self.start, [self.start])]
        while queue:
            node, path = queue.pop(0)
            if node == self.goal:
                return path
            visited.add(node)
            for neighbor in self.graph:
                if isinstance(neighbor, tuple) and neighbor[0] == node and neighbor[1] not in visited:
                    queue.append((neighbor[1], path + [neighbor[1]]))
        return None

# Example usage
start = (10, 10)
goal = (80, 30)
obstacles = [(20, 10, 20, 50), (20, 50, 90, 50), (30, 30, 40, 40)]

prm = PRM(start, goal, obstacles)
prm.build_roadmap()
path = prm.get_path()

if path:
    print("Path found:")
    print(path)
else:
    print("No path found.")
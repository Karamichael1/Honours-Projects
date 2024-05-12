import math

dataset = [
    [0.22, 0.33],
    [0.45, 0.76],
    [0.73, 0.39],
    [0.25, 0.35],
    [0.51, 0.69],
    [0.69, 0.42],
    [0.41, 0.49],
    [0.15, 0.29],
    [0.81, 0.32],
    [0.50, 0.88],
    [0.23, 0.31],
    [0.77, 0.30],
    [0.56, 0.75],
    [0.11, 0.38],
    [0.81, 0.33],
    [0.59, 0.77],
    [0.10, 0.89],
    [0.55, 0.09],
    [0.75, 0.35],
    [0.44, 0.55]
]

def euclidean_distance(x, y):
    ans = math.sqrt((x[0] - y[0])**2 + (x[1] - y[1])**2)
    return ans

def k_means(dataset, initial_centroids):
    centroids = initial_centroids
    while True:
        clusters = [[] for _ in range(len(centroids))]
        for point in dataset:
            distances = [euclidean_distance(point, centroid) for centroid in centroids]
            cluster_index = distances.index(min(distances))
            clusters[cluster_index].append(point)
        
        new_centroids = []
        for cluster in clusters:
            if len(cluster) > 0:
                new_centroid = [sum(x)/len(cluster) for x in zip(*cluster)]
                new_centroids.append(new_centroid)
        
        if centroids == new_centroids:
            break
        centroids = new_centroids
    
    
    non_empty_clusters = [cluster for cluster in clusters if len(cluster) > 0]
    non_empty_centroids = [centroid for centroid, cluster in zip(centroids, clusters) if len(cluster) > 0]
    
    return non_empty_centroids, non_empty_clusters

def sum_of_squares_error(clusters, centroids):
    error = 0
    for i in range(len(clusters)):
        for point in clusters[i]:
            error += euclidean_distance(point, centroids[i])**2
    return error

initial_centroids = []
for _ in range(3):
    x = float(input())
    y = float(input())
    initial_centroids.append([x, y])

final_centroids, clusters = k_means(dataset, initial_centroids)
error = sum_of_squares_error(clusters, final_centroids)
print(round(error, 4))
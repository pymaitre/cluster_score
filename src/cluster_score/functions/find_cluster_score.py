import numpy as np

def dfs(matrix, x, y, visited, cluster):
    # Directions for movement: right, down, left, up, and the four diagonal directions
    directions = [
        (0, 1),   # right
        (1, 0),   # down
        (0, -1),  # left
        (-1, 0),  # up
        (1, 1),   # down-right
        (1, -1),  # down-left
        (-1, 1),  # up-right
        (-1, -1)  # up-left
    ]
    
    visited[x][y] = True
    cluster.append((x, y))

    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        
        # Check boundaries and whether the new cell is part of the cluster
        if (0 <= new_x < matrix.shape[0] and
            0 <= new_y < matrix.shape[1] and
            not visited[new_x][new_y] and
            matrix[new_x][new_y] > 129):
            dfs(matrix, new_x, new_y, visited, cluster)

def find_clusters(matrix, threshold):
    visited = np.zeros(matrix.shape, dtype=bool)
    clusters = []
    
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i][j] > threshold and not visited[i][j]: 
                cluster = []
                dfs(matrix, i, j, visited, cluster)
                if len(cluster) >= 4: 
                    clusters.append(cluster)
    
    return clusters
   

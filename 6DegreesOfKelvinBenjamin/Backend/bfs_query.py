import pickle
from collections import deque

with open("../website/player_graph.pkl", "rb") as f:
    graph = pickle.load(f)

def bfs_path_with_metadata(graph, start, target):
    if start == target:
        return [start]

    visited = set()
    queue = deque([(start, [start])])
    parent = {start: None}

    while queue:
        current, path = queue.popleft()
        visited.add(current)

        for neighbor in graph[current]:
            if neighbor not in visited:
                parent[neighbor] = current
                if neighbor == target:
                    return reconstruct_path_with_edges(graph, parent, start, target)
                queue.append((neighbor, path + [neighbor]))
                visited.add(neighbor)

    return None

def reconstruct_path_with_edges(graph, parent, start, end):
    path = []
    current = end

    while current != start:
        prev = parent[current]
        connection = graph[prev][current]
        path.append((prev, current, connection))
        current = prev

    return path[::-1]


start_player = "RobiBi01"
end_player   = "BradTo00"

path = bfs_path_with_metadata(graph, start_player, end_player)

if path:
    print(f"\nPath from {start_player} to {end_player}:\n")
    for p1, p2, (teams, year) in path:
        print(f"{p1} -> {p2} via: {teams.upper()} {year}")
else:
    print("No path found between the two players.")

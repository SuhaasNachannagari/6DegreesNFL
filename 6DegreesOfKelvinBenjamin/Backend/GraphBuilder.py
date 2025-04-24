from nfl_data_py import import_weekly_data
from collections import defaultdict, deque
print(1)
'''
# 1. Load the weekly data (1999–2023) with the required columns
years = list(range(1999, 2024))
weekly_df = import_weekly_data(
    years=years,
    columns=["player_id", "recent_team", "season", "week"],
    downcast=True
)


# 2. Build the player graph with connection details
def build_player_graph_with_info(weekly_df):
    """
    Build a graph where:
      - Keys: player IDs (from "player_id")
      - Values: lists of tuples representing an edge.
        Each tuple is (neighboring_player_id, season, recent_team),
        indicating that the two players shared a game during that season on that team.
    """
    game_to_players = defaultdict(set)
    graph = defaultdict(list)

    # Group players by game using (season, week, recent_team)
    for _, row in weekly_df.iterrows():
        player_id = row["player_id"]
        game_key = (row["season"], row["week"], row["recent_team"])
        game_to_players[game_key].add(player_id)

    # For each game, connect each pair of players with (season, recent_team)
    for game_key, players in game_to_players.items():
        season, week, team = game_key  # We only need season and team for connection info
        for player in players:
            for teammate in players:
                if player != teammate:
                    # Append a connection from player -> teammate with the associated details
                    graph[player].append((teammate, season, team))

    return graph


# Build the graph once at startup
player_graph = build_player_graph_with_info(weekly_df)
print("Graph built with connection info.")


# 3. Breadth-First Search with Edge Details
def find_shortest_path_with_info(graph, start_id, end_id):
    """
    Finds the shortest path from start_id to end_id.
    Each step in the returned path is a tuple:
      (current_player_id, connection_info)
    For the starting node, connection_info is set to None.
    For subsequent nodes, connection_info is a tuple: (season, team)
    """
    visited = set()
    # Initialize the queue with a path containing the starting node; no connection info for start.
    queue = deque([[(start_id, None)]])

    while queue:
        path = queue.popleft()
        current, _ = path[-1]
        if current == end_id:
            return path

        if current not in visited:
            visited.add(current)
            # Expand the neighbors: Each edge holds (neighbor, season, team)
            for neighbor, season, team in graph.get(current, []):
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append((neighbor, (season, team)))
                    queue.append(new_path)
    return None


# 4. Display the path with connection details
def display_path_with_info(path):
    """
    Prints the path so that each connection is labeled with the season and team.
    The output format:
      PlayerA --(season, team)--> PlayerB --(season, team)--> PlayerC
    """
    if not path:
        print("No connection found.")
        return

    output = []
    for i, (player, info) in enumerate(path):
        if i == 0:
            output.append(f"{player}")
        else:
            season, team = info
            output.append(f"--({season}, {team})--> {player}")
    print(" ".join(output))


# 5. Example usage:
# Replace these with valid player IDs from your data.
start_id = input("Enter the start player's GSIS ID: ").strip()
end_id = input("Enter the end player's GSIS ID: ").strip()

path_with_info = find_shortest_path_with_info(player_graph, start_id, end_id)
display_path_with_info(path_with_info) 

'''

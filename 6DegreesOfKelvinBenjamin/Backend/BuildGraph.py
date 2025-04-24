import json
import pickle
from collections import defaultdict

# === FIX: Named functions instead of lambdas for pickle ===
def default_edge_list():
    return defaultdict(list)

def default_graph():
    return defaultdict(default_edge_list)

# === Load raw logs ===
with open("test.json", "r") as f:
    team_game_logs = json.load(f)

# === Combine home & away into full games ===
def group_full_games(team_game_logs):
    game_map = defaultdict(lambda: {
        "season": None,
        "date": None,
        "teams": set(),
        "players": set()
    })

    for record in team_game_logs:
        key = record["game_key"]
        game_map[key]["season"] = record["season"]
        game_map[key]["date"] = record["date"]
        game_map[key]["teams"].add(record["team"])
        game_map[key]["players"].update(record["players"])

    return game_map.values()

# === Build graph ===
def build_player_graph(full_games):
    graph = defaultdict(dict)  # no nested defaultdict needed anymore

    for game in full_games:
        players = list(game["players"])
        teams = ','.join(sorted(game["teams"]))
        year = game["season"]
        connection = (teams, year)

        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1, p2 = players[i], players[j]
                # Only add if not already connected
                if p2 not in graph[p1]:
                    graph[p1][p2] = connection
                    graph[p2][p1] = connection

    return graph


# === Execute and save ===
print("🔄 Grouping full games...")
full_games = group_full_games(team_game_logs)

print("🔗 Building player graph...")
graph = build_player_graph(full_games)

print("💾 Saving graph to disk...")
with open("../website/player_graph.pkl", "wb") as f:
    pickle.dump(dict(graph), f)  # convert top-level defaultdict to dict

print("✅ Done. Graph stored as 'player_graph.pkl'")

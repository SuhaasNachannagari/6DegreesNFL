import json
import pickle
from collections import defaultdict

def default_edge_list():
    return defaultdict(list)

def default_graph():
    return defaultdict(default_edge_list)

with open("test.json", "r") as f:
    team_game_logs = json.load(f)

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

def build_player_graph(full_games):
    graph = defaultdict(dict)
    for game in full_games:
        players = list(game["players"])
        teams = ','.join(sorted(game["teams"]))
        year = game["season"]
        connection = (teams, year)

        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                p1, p2 = players[i], players[j]
                if p2 not in graph[p1]:
                    graph[p1][p2] = connection
                    graph[p2][p1] = connection

    return graph



full_games = group_full_games(team_game_logs)
graph = build_player_graph(full_games)

with open("../website/player_graph.pkl", "wb") as f:
    pickle.dump(dict(graph), f)

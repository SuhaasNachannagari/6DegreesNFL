# website/views.py
from flask import (
    Blueprint, current_app,
    render_template, request, jsonify
)
from collections import deque

main_bp = Blueprint("main", __name__)

def get_team_name_for_year(code: str, year: int) -> str:
    code = code.upper()
    relocations = {
        "CRD": [
            {"from": 1960, "to": 1987, "name": "St. Louis Cardinals"},
            {"from": 1988, "to": 1993, "name": "Phoenix Cardinals"},
            {"from": 1994, "to": 2024, "name": "Arizona Cardinals"},
        ],
        "ATL": [
            {"from": 1960, "to": 2024, "name": "Atlanta Falcons"}
        ],
        "BAL": [
            {"from": 1996, "to": 2024, "name": "Baltimore Ravens"}
        ],
        "BUF": [
            {"from": 1960, "to": 2024, "name": "Buffalo Bills"}
        ],
        "CAR": [
            {"from": 1995, "to": 2024, "name": "Carolina Panthers"}
        ],
        "CHI": [
            {"from": 1922, "to": 2024, "name": "Chicago Bears"}
        ],
        "CIN": [
            {"from": 1968, "to": 2024, "name": "Cincinnati Bengals"}
        ],
        "CLE": [
            {"from": 1946, "to": 2024, "name": "Cleveland Browns"}
        ],
        "DAL": [
            {"from": 1946, "to": 2024, "name": "Dallas Cowboys"}
        ],
        "DET": [
            {"from": 1934, "to": 2024, "name": "Detroit Lions"}
        ],
        "GNB": [
            {"from": 1921, "to": 2024, "name": "Green Bay Packers"}
        ],
        "HTX": [
            {"from": 2002, "to": 2024, "name": "Houston Texans"}
        ],
        "CLT": [
            {"from": 1953, "to": 1983, "name": "Baltimore Colts"},
            {"from": 1954, "to": 2024, "name": "Indianapolis Colts"},
        ],
        "JAX": [
            {"from": 1995, "to": 2024, "name": "Jaxsonville Jaguars"}
        ],
        "KAN": [
            {"from": 1963, "to": 2024, "name": "Kansas City Chiefs"}
        ],
        "RAI": [
            {"from": 1966, "to": 1981, "name": "Oakland Raiders"},
            {"from": 1982, "to": 1994, "name": "Los Angeles Raiders"},
            {"from": 1995, "to": 2019, "name": "Oakland Raiders"},
            {"from": 2020, "to": 2024, "name": "Las Vegas Raiders"},
        ],
        "SDG": [
            {"from": 1961, "to": 2016, "name": "San Diego Chargers"},
            {"from": 2017, "to": 2024, "name": "Los Angeles Chargers"}
        ],
        "RAM": [
            {"from": 1946, "to": 1994, "name": "Los Angeles Rams"},
            {"from": 1995, "to": 2015, "name": "St. Louis Rams"},
            {"from": 2016, "to": 9999, "name": "Los Angeles Rams"},
        ],
        "MIA": [
            {"from": 2966, "to": 2024, "name": "Miami Dolphins"}
        ],
        "MIN": [
            {"from": 1961, "to": 2024, "name": "Minnesota Vikings"}
        ],
        "NWE": [
            {"from": 19600, "to": 1970, "name": "Boston Patriots"},
            {"from": 1961, "to": 2024, "name": "New England Patriots"},
        ],
        "NOR": [
            {"from": 1967, "to": 2024, "name": "New Orleans Saints"}
        ],
        "NYG": [
            {"from": 1925, "to": 2024, "name": "New York Giants"}
        ],
        "NYJ": [
            {"from": 1963, "to": 2024, "name": "New York Jets"}
        ],
        "PHI": [
            {"from": 1933, "to": 2024, "name": "Philadelphia Eagles"}
        ],
        "PIT": [
            {"from": 1945, "to": 2024, "name": "Pittsburgh Steelers"}
        ],
        "SFO": [
            {"from": 1946, "to": 2024, "name": "San Francisco 49ers"}
        ],
        "SEA": [
            {"from": 1976, "to": 2024, "name": "Seattle Seahawks"}
        ],
        "TAM": [
            {"from": 1976, "to": 2024, "name": "Tampa Bay Buccaneers"}
        ],
        "OTI": [
            {"from": 1960, "to": 1996, "name": "Houston Oilers"},
            {"from": 1997, "to": 1998, "name": "Tennessee Oilers"},
            {"from": 1999, "to": 2024, "name": "Tennessee Titans"},
        ],
        "WAS": [
            {"from": 1937, "to": 2019, "name": "Washington Redskins"},
            {"from": 2020, "to": 2021, "name": "Washington Football Team"},
            {"from": 2022, "to": 2024, "name": "Washington Commanders"},
        ],
    }

    if code in relocations:
        for era in relocations[code]:
            if era["from"] <= year <= era["to"]:
                return era["name"]

    # fallback to your static mapping for all other codes
    return current_app.team_names.get(code, code)

def bfs_path_with_metadata(graph, start, target):
    if start == target:
        return []
    visited = {start}
    queue = deque([start])
    parent = {start: None}

    while queue:
        curr = queue.popleft()
        for neigh in graph[curr]:
            if neigh not in visited:
                parent[neigh] = curr
                if neigh == target:
                    return reconstruct_path_with_edges(graph, parent, start, target)
                visited.add(neigh)
                queue.append(neigh)
    return None

def reconstruct_path_with_edges(graph, parent, start, end):
    path = []
    curr = end
    while curr != start:
        prev = parent[curr]
        teams, year = graph[prev][curr]
        path.append((prev, curr, teams.upper(), year))
        curr = prev
    path.reverse()
    return path

@main_bp.route("/", methods=["GET", "POST"])
def home():
    error = None
    rendered_steps = []

    if request.method == "POST":
        # grab exactly what was set in your hidden inputs
        start  = request.form.get("start", "").strip()
        target = request.form.get("target", "").strip()
        graph  = current_app.graph

        if not start or not target:
            error = "Please select both players from the dropdown."
        elif start not in graph or target not in graph:
            error = "One or both player codes not found."
        else:
            raw_path = bfs_path_with_metadata(graph, start, target)
            if raw_path is None:
                error = f"No connection found between {start} and {target}."
            else:
                pm = current_app.players_map
                for c1, c2, code, year_str in raw_path:
                    year = int(year_str)
                    rendered_steps.append({
                        "p1":   pm.get(c1, {}).get("name", c1),
                        "p2":   pm.get(c2, {}).get("name", c2),
                        "team": get_team_name_for_year(code, year),
                        "code": code,   # keep original mixed-case
                        "year": year_str
                    })

    return render_template(
        "home.html",
        path=rendered_steps,
        error=error
    )



@main_bp.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "").lower()
    results = []
    for p in current_app.players:
        if q in p["name"].lower():
            label = f"{p['name']} — {p['pos']} ({p['from']}-{p['to']})"
            results.append({
                "label": label,
                "code":  p["code"],
                "pos":   p["pos"]
            })
            if len(results) >= 10:
                break
    return jsonify(results)

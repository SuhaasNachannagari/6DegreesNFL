# website/__init__.py
import os
import json
import pickle
import gzip
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates"
    )

    # — Load your graph, preferring a gzipped version if present —
    base_dir  = os.path.dirname(__file__)
    gz_path   = os.path.join(base_dir, "player_graph.pkl.gz")
    raw_path  = os.path.join(base_dir, "player_graph.pkl")


    loader, path = gzip.open, gz_path


    with loader(path, "rb") as f:
        app.graph = pickle.load(f)

    # — Load & filter players.json —
    players_path = os.path.join(base_dir, "players.json")
    with open(players_path, "r") as f:
        raw_players = json.load(f)

    # only keep those whose last season (p["to"]) is 1966 or later
    app.players = [
        p for p in raw_players
        if int(p["to"]) >= 1966
    ]
    app.players_map = { p["code"]: p for p in app.players }

    # — Fallback team‐names mapping —
    app.team_names = {
        "CRD": "Arizona Cardinals",
        "ATL": "Atlanta Falcons",
        "BAL": "Baltimore Ravens",
        "BUF": "Buffalo Bills",
        "CAR": "Carolina Panthers",
        "CHI": "Chicago Bears",
        "CIN": "Cincinnati Bengals",
        "CLE": "Cleveland Browns",
        "DAL": "Dallas Cowboys",
        "DEN": "Denver Broncos",
        "DET": "Detroit Lions",
        "GNB": "Green Bay Packers",
        "HTX": "Houston Texans",
        "CLT": "Indianapolis Colts",
        "JAX": "Jacksonville Jaguars",
        "KAN": "Kansas City Chiefs",
        "RAI": "Las Vegas Raiders",
        "SDG": "Los Angeles Chargers",
        "RAM": "Los Angeles Rams",
        "MIA": "Miami Dolphins",
        "MIN": "Minnesota Vikings",
        "NWE": "New England Patriots",
        "NOR": "New Orleans Saints",
        "NYG": "New York Giants",
        "NYJ": "New York Jets",
        "PHI": "Philadelphia Eagles",
        "PIT": "Pittsburgh Steelers",
        "SFO": "San Francisco 49ers",
        "SEA": "Seattle Seahawks",
        "TAM": "Tampa Bay Buccaneers",
        "OTI": "Tennessee Titans",
        "WAS": "Washington Commanders",
    }

    # — Register blueprints —
    from .views import main_bp
    app.register_blueprint(main_bp)

    return app

# 6 Degrees of Kelvin Benjamin

**6 Degrees of Kelvin Benjamin** is a Flask-based web application that models NFL player connectivity using graph theory. Inspired by the "Six Degrees of Kevin Bacon" concept, the tool allows users to query how two NFL players are connected via shared team-game appearances. The project combines large-scale web scraping, efficient graph construction, and an interactive frontend to deliver fast, explainable results.

---

## Project Motivation

The NFL is a highly interconnected ecosystem. Players move between teams, line up beside future Hall-of-Famers, and share the field with rising rookies. This project explores that network by asking: _“Can you trace a path between any two NFL players through shared team-game appearances?”_

The goal is to visualize the implicit connections between players across generations and rosters using actual participation data — not just rosters or transactions.

---

## Technical Overview

At its core, the application builds and queries a graph where:

- **Nodes** represent individual NFL players.
- **Edges** connect players who played in the **same game** for the **same team**.

A precomputed graph is serialized using `pickle`, and shortest paths are retrieved in real time via **Breadth-First Search (BFS)**. The backend is served using Flask, and the frontend includes a player search interface with autocomplete functionality.


## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/6DegreesNFL.git
   cd 6DegreesNFL
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flask --app 6DegreesOfKelvinBenjamin.main run
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

---

## Web Scraping Process

This project would not be possible without access to comprehensive historical game data. The player graph is built using data scraped directly from [Pro Football Reference](https://www.pro-football-reference.com/), covering the period from 1999 through 2024.

Scraping involved:

- Visiting over **30,000 game pages** to extract team-level player participation.
- Parsing and standardizing HTML tables across inconsistent formats.
- Mapping player names to stable PFR IDs to ensure consistent tracking across seasons.
- Implementing rate limiting and checkpointing to avoid server blocks and recover from failures.

This was a non-trivial engineering task that required building resilient scraping pipelines, developing robust parsers for edge cases, and resolving ambiguities between similarly named players.

The output of this pipeline includes:
- `players.json` containing metadata for all identified players.
- `player_graph.pkl` as a compact representation of the full connectivity graph.

---

## Key Features

- **Efficient Graph Querying**: All results are computed on a prebuilt graph using BFS for low-latency pathfinding.
- **Real Game Participation Only**: Connections reflect players who actually took the field, not just those on the roster.
- **Interactive UI**: A simple, autocomplete-enabled frontend makes it easy to explore the graph.
- **Robust Data Model**: Player connections persist even across team or season changes.

---

## Example Use Case

> _How is Travis Hunter (2025) connected to Tom Brady?_

The system might return:
```
Travis Hunter → DeAndre Hopkins → Larry Fitzgerald → Kurt Warner → Tom Brady  
Shortest path length: 4
```

This type of query demonstrates how a recent player can be traced through multiple generations of NFL stars.

---

## Data Rules and Assumptions

- Only regular season and postseason games from 1999 onward are included.
- Edges only form between players on the **same team in the same game**.
- Players are identified by unique PFR slugs (e.g., `CoopAm00` for Amari Cooper).
- Graph includes only players who actually appeared in at least one game.

---

## Potential Enhancements

- Show season/game metadata for each edge in the returned path.
- Add filters by position (e.g., WR-only paths).
- Support connections across different team stints (e.g., trade chains).
- Deploy the site publicly with persistent storage and a CI/CD pipeline.

---

## License

This project is intended for academic and demonstrative use only.  
All data is sourced from Pro Football Reference (PFR), which is the property of Sports Reference LLC.  
No commercial usage or redistribution of scraped data is permitted.

---

## Contact

For questions, feedback, or contributions, please open an issue or contact the repository maintainer.

# 6 Degrees of Kelvin Benjamin

**6 Degrees of Kelvin Benjamin** is a Flask-based web application that models NFL player connectivity using graph theory. Inspired by the "Six Degrees of Kevin Bacon" concept, the tool allows users to query how two NFL players are connected via shared team-game appearances. The project combines large-scale web scraping, efficient graph construction, and an interactive frontend to deliver fast, explainable results.

---

## Project Motivation

The NFL is a highly interconnected ecosystem. Players move between teams, line up beside future Hall-of-Famers, and share the field with rising rookies. This project explores that network by asking: _“Can you trace a path between any two NFL players through shared team-game appearances?”_ The user becomes more informed about the history of this beautiful game, and a mini-game lies where you can try to find players that are ATLEAST 5 degrees apart. Congratulations if you manage to get to 6, it's considered nearly impossible. And anything past that? Good luck.

A key trait of this specific application is to visualize the implicit connections between players across generations and rosters using actual participation data — not just rosters or transactions. It made the process of consolidating everything that much harder, but it is the only way to account for trades and make the system wholly accurate - we do not want to say that 2 players traded for one another, however rare that may be in the NFL, shared the field together. However roster data per year would have it so both played on the Jaguars in 2023 for example, thus we need to take the extra, painful precaution of analyzing individual game logs and all participants.

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
   pip install flask jinja2 requests beautifulsoup4 lxml
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

This project would not be possible without access to comprehensive historical game data. The player graph is built using data scraped directly from [Pro Football Reference](https://www.pro-football-reference.com/), covering the period from 1967 through 2024, aka the creation of the modern NFL as we know it through a merger. I complied by the rate limits out of respect for the very kind people over at PFR, regardless of how much time it took me (it took days of my computer just running and running, none of my friends wanted to help me out :( ).

Scraping involved:

- Visiting over **30,000 game pages** to extract team-level player participation.
- Parsing and standardizing HTML tables across inconsistent formats.
- Mapping player names to stable PFR IDs to ensure consistent tracking across seasons.
- Implementing rate limiting and checkpointing to avoid server blocks and recover from failures.

This was a non-trivial engineering task that required building resilient scraping pipelines, developing robust parsers for edge cases such as missing tables in a given page due to just human stat-coleection errors, and resolving ambiguities between similarly named players by scraping PFR for another dataset with every player mapped to their pfr_id.

The output of this pipeline includes:
- `players.json` containing metadata for all identified players and their pfr_ids, used for the autocomplete dropdown on the website.
- `player_graph.pkl` as a compact representation of the full connectivity graph, which we almost unzip and utilize to find the shortest path.

---

## Key Features

- **Efficient Graph Querying**: All results are computed on a prebuilt graph using BFS for low-latency pathfinding. This graph will have to be updated every year, or every week if I find the strength and patience in me to scrape that data.
- **Real Game Participation Only**: Connections reflect players who actually took the field (even if they did not play any minutes), not just those on the roster. Apologies in advance for anyone trying to use J.J. McCarthy, I know how much of a bummer it is, but you will have to wait until he plays one game atleast. Maybe I might include preseason someday, but for now I did both regular season, and the very difficult and inconsistent post-season implementation. I will be taking a break.
- **Interactive UI**: A simple, autocomplete-enabled frontend makes it easy to explore the graph using the BFS.
- **Robust Data Model**: Player connections persist even across team or season changes, game logs are very static.

---

## Example Use Case

> _How is Tom Brady connected to Dan Marino?_

The system might return:
<img width="506" alt="image" src="https://github.com/user-attachments/assets/584dfa26-d22d-4a23-a71b-346b898ff3c7" />


This type of query demonstrates how a recent player can be traced through multiple generations of NFL stars. It can get much longer than this, but those paths are for the users to find out :) Good luck getting to 6 or more connections.

---

## Data Rules and Assumptions

- Only regular season and postseason games from 1967 onward are included.
- Edges only form between players on the **same team in the same game**.
- Players are identified by unique PFR slugs (e.g., `CoopAm00` for Amari Cooper).
- Graph includes only players who actually appeared in at least one game.

---

## Potential Enhancements

- My top priority is creating a guessing game almost, where my data can be repurposed to allow the users to get from one random player to another random player in the fewest teammates possible. This should be easier because there's no pathfinding, it is just take input, check for gamelog with both players, verify, and repeat.
- Show season/game metadata for each edge in the returned path.
- Add filters by position (e.g., WR-only paths).
- Support connections across different team stints (e.g., trade chains).
- Deploy the site publicly with persistent storage and a CI/CD pipeline.

---

## License

This project is intended for academic and demonstrative use only.  
All data is sourced from Pro Football Reference (PFR), which is the property of Sports Reference LLC.  

---

## Contact

For questions, feedback, or contributions, please feel free to reach out to me at madhusuhaas@gmail.com, or my [linkedin](https://www.pro-football-reference.com/)


# 6 Degrees of Kelvin Benjamin 🏈

A "Six Degrees of Kevin Bacon"–style web app that connects NFL players through shared game appearances — revealing how closely linked your favorite players are.

## Overview

**6 Degrees of Kelvin Benjamin** is a graph-based exploration tool for NFL fans. It answers questions like:  
> *"How is Tom Brady connected to Travis Hunter?" or go a little further: "How is Saquon Barkley connected to Walter Payton*   

By analyzing real NFL game data since 1966, the app constructs a massive player graph where edges connect players who appeared **in the same game** for **the same team**.

## Features

- 🔍 Search any two players (from 1999 onward)
- 🔗 Find shortest path of shared games/teams between them
- 🧠 Backend graph construction using BFS
- 📊 Scraped data from Pro Football Reference (PFR)
- 💻 Frontend UI with player autocompletion

## Tech Stack

- **Python**: graph building, BFS search
- **Flask**: lightweight web framework
- **HTML/CSS + JavaScript**: frontend + autocomplete UX
- **Pickle / JSON**: data serialization
- **Pro Football Reference**: data source

## Setup Instructions

1. **Clone this repo**  
   ```bash
   git clone https://github.com/your-username/6DegreesOfKelvinBenjamin.git
   cd 6DegreesOfKelvinBenjamin

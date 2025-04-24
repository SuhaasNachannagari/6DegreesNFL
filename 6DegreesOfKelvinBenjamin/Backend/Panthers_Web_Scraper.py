import requests
from bs4 import BeautifulSoup, Comment
import re
import time
import json

BASE_URL       = "https://www.pro-football-reference.com"
DELAY_SECONDS  = 2.5
TEAM_CODE      = "car"
START_YEAR     = 1995
END_YEAR       = 2024
CARDINALS_LOG_NAMES = {'CAR'}

KEYWORDS = [
    "passing", "rushing", "receiving",
    "defense", "fumbles",
    "kick", "punt", "return",
    "kicking", "punting"
]

def get_boxscore_links_for_team_year(team_abbr, year):
    url = f"{BASE_URL}/teams/{team_abbr}/{year}/gamelog/"
    print(f"Scraping gamelog: {url}")
    resp = requests.get(url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    pattern = re.compile(r"^/boxscores/\d{9}[a-z]{3}\.htm$")
    links = sorted({
        a["href"] for a in soup.find_all("a", href=True)
        if pattern.match(a["href"])
    })

    time.sleep(DELAY_SECONDS)
    return links

def all_tables_including_comments(soup):
    tables = soup.find_all("table")
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in comment:
            comment_soup = BeautifulSoup(comment, "html.parser")
            tables.extend(comment_soup.find_all("table"))
    return tables

def scrape_game_rosters(team, game_url, year):
    full_url = f"{BASE_URL}{game_url}"
    print(f"Fetching boxscore: {full_url}")
    resp = requests.get(full_url)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    m = re.search(r"/boxscores/(\d{4})(\d{2})(\d{2})", game_url)
    date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "unknown"

    player_ids = []
    for table in all_tables_including_comments(soup):
        cap = table.find("caption")
        if not cap or not any(kw in cap.get_text(strip=True).lower() for kw in KEYWORDS):
            continue
        for row in table.find("tbody").find_all("tr"):
            if row.get("class") and "thead" in row["class"]:
                continue
            tm_cell = row.find("td", {"data-stat": "team"})
            if not tm_cell:
                continue
            tm = tm_cell.get_text(strip=True)
            valid = (tm == 'CAR')
            if not valid:
                continue
            th = row.find("th", {"data-stat": "player"})
            if th and th.has_attr("data-append-csv"):
                player_ids.append(th["data-append-csv"])

    time.sleep(DELAY_SECONDS)
    unique_ids = list(dict.fromkeys(player_ids))
    if not unique_ids:
        return None

    return {
        "season": year,
        "game_key": f"{date_str}-{team}",
        "date": date_str,
        "team": team,
        "players": unique_ids
    }

if __name__ == "__main__":
    all_rosters = []
    for year in range(START_YEAR, END_YEAR + 1):
        links = get_boxscore_links_for_team_year(TEAM_CODE, year)
        print(f"\nYear {year}: found {len(links)} game(s).")
        for link in links:
            roster = scrape_game_rosters(TEAM_CODE, link, year)
            if roster:
                all_rosters.append(roster)

    output_path = "all_rosters.json"
    with open(output_path, "r", encoding="utf-8") as f:
        existing = json.load(f)

    existing.extend(all_rosters)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    print(f"Saved {len(all_rosters)} roster records to {output_path}")

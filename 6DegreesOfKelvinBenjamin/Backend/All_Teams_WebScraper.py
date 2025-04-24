import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup, Comment

# ---------- CONFIGURATION ----------
BASE_URL       = "https://www.pro-football-reference.com"
DELAY_SECONDS  = 3.5               # seconds between requests
START_YEAR     = 1966
END_YEAR       = 2024
OUTPUT_PATH    = "test.json"

# Table caption keywords to identify stat tables
KEYWORDS = [
    "passing", "rushing", "receiving",
    "defense", "fumbles",
    "kick", "punt", "return",
    "kicking", "punting"
]
'''
TEAM_YEAR_DISPLAY = {
    "cin": [(2020, 2020, {"CIN"})],
    "cle": [(2020, 2020, {"CLE"}),
            (1999, 1999, {"CLE"})],
    "dal": [(1966, 1966, {"DAL"})],
    "den": [(1966, 1966, {"DEN"})],
    "det": [(1966, 1966, {"DET"})],
    "gnb": [(1966, 1966, {"GNB"})],
    "htx": [(2002, 2002, {"HOU"})],
    "clt": [(1966, 1966, {"BAL"}),
            (1984, 1984, {"IND"})],
    "jax": [(1995, 1995, {"JAX"})],
    "kan": [(1966, 1966, {"KAN"})],
    "rai": [(1966, 1966, {"OAK"}),
            (1982, 1982, {"RAI"}),
            (1995, 1995, {"OAK"}),
            (2020, 2020, {"LVR"})],
    "sdg": [(1966, 1966, {"SDG"}),
            (2017, 2017, {"LAC"})],
    "ram": [(1966, 1966, {"RAM"}),
            (1995, 1995, {"STL"}),
            (2016, 2016, {"RAM"})],
    "mia": [(1966, 1966, {"MIA"})],
    "min": [(1966, 1966, {"MIN"})],
    "nwe": [(1966, 1966, {"BOS"}),
            (1971, 1971, {"NWE"})],
    "nor": [(1967, 1967, {"NOR"})],
    "nyg": [(1966, 1966, {"NYG"})],
    "nyj": [(1966, 1966, {"NYJ"})],
    "phi": [(1966, 1966, {"PHI"})],
    "pit": [(1966, 1966, {"PIT"})],
    "sea": [(1976, 1976, {"SEA"})],
    "sfo": [(1966, 1966, {"SFO"})],
    "tam": [(1976, 1976, {"TAM"})],
    "oti": [(1966, 1966, {"HOU"}),
            (1997, 1997, {"TEN"})],
    "was": [(1966, 1966, {"WAS"})],
}
'''
# Map each internal team code to a list of (start_year, end_year, valid display codes)
TEAM_YEAR_DISPLAY = {
    "crd": [(1966, 1987, {"STL"}),
            (1988, 1993, {"PHO"}),
            (1994, 2024, {"ARI"})],
    "atl": [(1966, 2024, {"ATL"})],
    "rav": [(1996, 2024, {"BAL"})],
    "buf": [(1966, 2024, {"BUF"})],
    "car": [(1995, 2024, {"CAR"})],
    "chi": [(1966, 2024, {"CHI"})],
    "cin": [(1968, 2024, {"CIN"})],
    "cle": [(1966, 1995, {"CLE"}),
            (1999, 2024, {"CLE"})],
    "dal": [(1966, 2024, {"DAL"})],
    "den": [(1966, 2024, {"DEN"})],
    "det": [(1966, 2024, {"DET"})],
    "gnb": [(1966, 2024, {"GNB"})],
    "htx": [(2002, 2024, {"HOU"})],
    "clt": [(1966, 1983, {"BAL"}),
            (1984, 2024, {"IND"})],
    "jax": [(1995, 2024, {"JAX"})],
    "kan": [(1966, 2024, {"KAN"})],
    "rai": [(1966, 1981, {"OAK"}),
            (1982, 1994, {"RAI"}),
            (1995, 2019, {"OAK"}),
            (2020, 2024, {"LVR"})],
    "sdg": [(1966, 2016, {"SDG"}),
            (2017, 2024, {"LAC"})],
    "ram": [(1966, 1994, {"RAM"}),
            (1995, 2015, {"STL"}),
            (2016, 2024, {"RAM"})],
    "mia": [(1966, 2024, {"MIA"})],
    "min": [(1966, 2024, {"MIN"})],
    "nwe": [(1966, 1970, {"BOS"}),
            (1971, 2024, {"NWE"})],
    "nor": [(1967, 2024, {"NOR"})],
    "nyg": [(1966, 2024, {"NYG"})],
    "nyj": [(1966, 2024, {"NYJ"})],
    "phi": [(1966, 2024, {"PHI"})],
    "pit": [(1966, 2024, {"PIT"})],
    "sea": [(1976, 2024, {"SEA"})],
    "sfo": [(1966, 2024, {"SFO"})],
    "tam": [(1976, 2024, {"TAM"})],
    "oti": [(1966, 1996, {"HOU"}),
            (1997, 2024, {"TEN"})],
    "was": [(1966, 2024, {"WAS"})],
}

TEAM_CODES = list(TEAM_YEAR_DISPLAY.keys())

def valid_display_codes(team: str, year: int):
    for start, end, codes in TEAM_YEAR_DISPLAY.get(team, []):
        if start <= year <= end:
            return codes
    return None


def fetch_url(url: str):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    time.sleep(DELAY_SECONDS)
    return resp


def get_boxscore_links(team: str, year: int):
    url = f"{BASE_URL}/teams/{team}/{year}/gamelog/"
    print(f"Fetching gamelog: {url}")
    soup = BeautifulSoup(fetch_url(url).text, "html.parser")
    pattern = re.compile(r"^/boxscores/\d{9}[a-z]{3}\.htm$")
    links = sorted({a["href"] for a in soup.find_all("a", href=True) if pattern.match(a["href"])})
    print(f"  Found {len(links)} boxscore links for {team} {year}")
    return links


def all_tables_including_comments(soup: BeautifulSoup):
    tables = soup.find_all("table")
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in c:
            inner = BeautifulSoup(c, "html.parser")
            comment_tables = inner.find_all("table")
            tables.extend(comment_tables)
    return tables


def get_snap_table(soup: BeautifulSoup, team: str, game_url: str):
    code = game_url.split("/")[-1][9:12]
    print(code)
    div_id = "all_home_snap_counts" if code.upper() == team.upper() else "all_vis_snap_counts"
    wrapper = soup.find("div", id=div_id)
    if wrapper:
        print(f"    Snaps div '{div_id}' found live")
    else:
        # try comments
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            if div_id in c:
                inner = BeautifulSoup(c, "html.parser")
                wrapper = inner.find("div", id=div_id)
                if wrapper:
                    break
    if not wrapper:
        print(f"    Snaps div '{div_id}' NOT found")
        return None
    tbl = wrapper.find("table")
    if tbl:
        print(f"    Snaps table under '{div_id}' found")
        return tbl
    for c in wrapper.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in c:
            tbl = BeautifulSoup(c, "html.parser").find("table")
            if tbl:
                print(f"    Starters table under '{div_id}' found in comments")
                return tbl
    print(f"    Starters table under '{div_id}' NOT found")
    return None


def get_starters_table(soup: BeautifulSoup, team: str, game_url: str):
    code = game_url.split("/")[-1][9:12]
    print(code)
    div_id = "all_home_starters" if code.upper() == team.upper() else "all_vis_starters"
    wrapper = soup.find("div", id=div_id)
    if wrapper:
        print(f"    Starters div '{div_id}' found live")
    else:
        # try comments
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            if div_id in c:
                inner = BeautifulSoup(c, "html.parser")
                wrapper = inner.find("div", id=div_id)
                if wrapper:
                    print(f"    Starters div '{div_id}' found in comments")
                    break
    if not wrapper:
        print(f"    Starters div '{div_id}' NOT found")
        return None
    tbl = wrapper.find("table")
    if tbl:
        print(f"    Starters table under '{div_id}' found")
        return tbl
    for c in wrapper.find_all(string=lambda t: isinstance(t, Comment)):
        if "<table" in c:
            tbl = BeautifulSoup(c, "html.parser").find("table")
            if tbl:
                print(f"    Starters table under '{div_id}' found in comments")
                return tbl
    print(f"    Starters table under '{div_id}' NOT found")
    return None

def scrape_rosters_for_team(team: str):
    docs = []
    for year in range(START_YEAR, END_YEAR + 1):
        codes = valid_display_codes(team, year)
        if not codes:
            continue
        links = get_boxscore_links(team, year)
        for link in links:
            url = BASE_URL + link
            print(f"\n--- Processing boxscore: {url}")
            soup = BeautifulSoup(fetch_url(url).text, "html.parser")
            m = re.search(r"/boxscores/(\d{4})(\d{2})(\d{2})", link)
            date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else "unknown"
            players = set()

            stat_found = 0
            for tbl in all_tables_including_comments(soup):
                cap = tbl.find("caption")
                if not cap:
                    continue
                cap_txt = cap.get_text(strip=True).lower()
                if not any(kw in cap_txt for kw in KEYWORDS):
                    continue
                stat_found += 1
                print(f"    STAT table '{cap.get_text(strip=True)}' matched (#{stat_found})")
                for row in tbl.find("tbody").find_all("tr"):
                    if row.get("class") and "thead" in row["class"]:
                        continue
                    td_team = row.find("td", {"data-stat": "team"})
                    if not td_team or td_team.get_text(strip=True) not in codes:
                        continue
                    th = row.find("th", {"data-stat": "player"})
                    if th and th.has_attr("data-append-csv"):
                        players.add(th["data-append-csv"])
            if stat_found == 0:
                print(f"    WARNING: no STAT tables matched for {team} {date_str}")

            snap_tbl = get_snap_table(soup, team, link)
            if snap_tbl:
                print(f"    Extracting {len(snap_tbl.find_all('tr'))} rows from snap counts")
            else:
                print("    No snap counts to extract")

            if snap_tbl:
                for row in snap_tbl.find("tbody").find_all("tr"):
                    if row.get("class") and "thead" in row["class"]:
                        continue
                    th = row.find("th", {"data-stat": "player"})
                    if th and th.has_attr("data-append-csv"):
                        players.add(th["data-append-csv"])

            starters_tbl = get_starters_table(soup, team, link)
            if starters_tbl:
                print(f"    Extracting {len(starters_tbl.find_all('tr'))} rows from starters")
            else:
                print("    No starters table to extract")

            if starters_tbl:
                for row in starters_tbl.find("tbody").find_all("tr"):
                    if row.get("class") and "thead" in row["class"]:
                        continue
                    th = row.find("th", {"data-stat": "player"})
                    if th and th.has_attr("data-append-csv"):
                        players.add(th["data-append-csv"])

            print(f"    Total unique players collected: {len(players)}")
            if players:
                docs.append({
                    "season": year,
                    "game_key": f"{date_str}-{team}",
                    "date": date_str,
                    "team": team,
                    "players": list(players)
                })
    return docs

# ---------- MAIN ----------
if __name__ == "__main__":
    if os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
            all_rosters = json.load(f)
    else:
        all_rosters = []
    done_teams = {d["team"] for d in all_rosters}
    to_do = [t for t in TEAM_CODES if t not in done_teams]
    print("Teams remaining:", to_do)
    for team in to_do:
        print(f"\n--- Scraping team: {team.upper()} ---")
        team_docs = scrape_rosters_for_team(team)
        if team_docs:
            all_rosters.extend(team_docs)
            with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
                json.dump(all_rosters, f, indent=2)
            print(f"Appended {len(team_docs)} records for {team.upper()}")
    print(f"\nAll done! Total records: {len(all_rosters)}")
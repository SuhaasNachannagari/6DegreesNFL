import requests
import json
import string
import re
from bs4 import BeautifulSoup

PLAYER_URL = "https://www.pro-football-reference.com/players/{letter}/"

RE = re.compile(r"""
    \(\s*
      (?P<pos>[^)]*)   
    \s*\)\s*
    (?P<year_from>\d{4})
    [–-]
    (?P<year_to>\d{4})
""", re.X)

def scrape_letter(letter):
    url = PLAYER_URL.format(letter=letter.upper())
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    container = soup.find("div", id="div_players")
    players = []
    for p in container.find_all("p"):
        a = p.find("a")
        if not a:
            continue

        name = a.text.strip()
        code = a["href"].split("/")[-1].replace(".htm", "")

        raw = p.get_text().replace(name, "", 1).strip().strip('"').strip()
        m = RE.search(raw)
        if not m:
            # you can log these if you like, but most should now match
            print(f"❗️ couldn't parse: {raw!r}")
            continue

        pos = m.group("pos").strip() or None
        year_from = m.group("year_from")
        year_to   = m.group("year_to")

        players.append({
            "code": code,
            "name": name,
            "pos": pos,           # will be None if empty
            "from": year_from,
            "to":   year_to
        })

    return players

def main():
    all_players = []
    for letter in string.ascii_lowercase:
        print(f"Scraping {letter.upper()} …")
        all_players.extend(scrape_letter(letter))
    print(f"Total players scraped: {len(all_players)}")

    with open("../website/players.json", "w") as f:
        json.dump(all_players, f, indent=2)
    print("→ Wrote players.json")

if __name__ == "__main__":
    main()

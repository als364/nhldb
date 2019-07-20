from requests import get
from requests.exceptions import RequestException

import csv
import time

import extract
import teams

def main():
  print(f"{time.asctime(time.localtime())}: Started scraping", flush=True)
  start = time.time()
  base_url = "https://www.hockey-reference.com"

  years = range(2015, 2020)
  serialized_games = []
  for year in years:
    urls_by_team = {team: f"{base_url}/teams/{team}/{year}_gamelog.html" for team in teams.team_name_by_abbr.keys()}
    for team, url in urls_by_team.items():
      print(f"{time.asctime(time.localtime())}: Scraping {team} games", flush=True)
      game_urls = extract.get_game_urls_from_gamelog(simple_get(url).content, base_url)
      for game_url in game_urls:
        print(f"{time.asctime(time.localtime())}: Scraping {game_url}", flush=True)
        (winner, loser, num_penalties) = extract.get_penalties_from_game(simple_get(game_url).content)
        serialized_games.append(serialize(winner, loser, num_penalties, game_url))
    deduped_serialized_games = set(serialized_games)

    with open(f"{year}.csv", 'w', newline="") as file:
      writer = csv.writer(file, delimiter=",")
      for serialized_game in deduped_serialized_games:
        # The things I do to not do work in Excel
        writer.writerow(serialized_game.split(","))
  end = time.time()
  print(f"Total time: {end-start}", flush=True)

def simple_get(url):
  try:
    response = get(url)
    content_type = response.headers['Content-Type'].lower()
    if (response.status_code == 200 and content_type is not None and content_type.find('html') > -1):
      return response
    else:
      print(f"wtf: {response}")
  except RequestException as e:
    print(f"Error during GET to {url}: {str(e)}", flush=True)

def serialize(winner, loser, num_penalties, game_url):
  game_id = game_url.split("/")[-1].split(".")[0]
  return f"{game_id},{winner},{loser},{num_penalties}"

###############################################################################
if __name__ == "__main__":
  main()

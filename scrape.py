from requests import get
from requests.exceptions import RequestException

import csv
import os
import time

import constants
import extract
import teams

def main():
  print(f"{stringy_now()}: Started scraping", flush=True)
  start = time.time()
  base_url = "https://www.hockey-reference.com"

  years = [year for year in range(constants.FIRST_YEAR, constants.PRESENT_YEAR + 1) if year not in constants.BROKEN_YEARS]
  for year in years:
    # TODO: are there duplicates here??
    maybe_make_directory(year)
    active_teams_by_abbr = {abbr: team for abbr, team in teams.teams_by_abbr().items() if team.stint_by_year(year) is not None}
    for abbr, team in active_teams_by_abbr.items():
      print(f"{stringy_now()}: Scraping {team.stint_by_year(year).abbr} games from {year}", flush=True)
      url = f"{base_url}/teams/{team.stint_by_year(year).abbr}/{year}_gamelog.html"
      (regular_season_urls, playoff_urls) = extract.get_game_urls_from_gamelog(simple_get(url), base_url)

      regular_season_filename = f"data/{year}/{abbr}.csv"
      # This is expensive, so we don't want to do it if we already have the data.
      if os.path.isfile(regular_season_filename):
        print(f"{regular_season_filename} already exists, skipping")
      else:
        regular_season_serialized_games = scrape(regular_season_urls)
        write_file(regular_season_serialized_games, regular_season_filename)

      playoff_filename = f"data/{year}/{abbr}_playoffs.csv"
      if os.path.isfile(playoff_filename):
        print(f"{playoff_filename} already exists, skipping")
      elif len(playoff_urls) == 0:
        print(f"{abbr} missed the playoffs in {year}, skipping")
      else:
        playoff_serialized_games = scrape(playoff_urls)
        write_file(playoff_serialized_games, playoff_filename)

  end = time.time()
  print(f"Total time: {end-start}", flush=True)

###############################################################################
# scrape_regular_season
#
# Scrapes a list of hockey-reference game urls for game data 
#
# Inputs:
#   base_url: The url of the scraped website because for SOME REASON these
#             hrefs are relative
#
# Outputs:
#   A list of lists of:
#     game_id: timestamp (YYYYMMDD) + 0 + home team, e.g. 201902230PHI
#     winner: the team that won the game
#     loser: the team that lost the game
#     num_penalties: the number of roughing/fighting penalties
###############################################################################
def scrape(urls):
    serialized_games = []
    for url in urls:
      if url not in broken_urls():
        print(f"{stringy_now()}: Scraping {url}", flush=True)
        game_html = simple_get(url)
        (winner, loser, num_penalties) = extract.get_penalties_from_game(game_html)
        serialized_games.append((winner, loser, num_penalties, url))
      else:
        print(f"{url} is broken, skipping...")

    # Dedupe.
    return set(serialized_games)

###############################################################################
# write_file
#
# Inputs:
#   serialized_games: An array of game information
#   filename: The name of the file to write to
#
# Outputs:
#   A list of urls of hockey-reference game pages played by that team
###############################################################################
def write_file(serialized_games, filename):
  # TODO: split by year and team instead of just year
  with open(filename, 'w', newline="") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow(["game_id", "winner", "loser", "num_penalties"])
    for (winner, loser, num_penalties, game_url) in serialized_games:
      game_id = game_url.split("/")[-1].split(".")[0]
      writer.writerow([game_id,winner,loser,num_penalties])

def maybe_make_directory(year):
  if(not os.path.exists(f"data/{year}")):
    os.mkdir(f"data/{year}")

###############################################################################
# simple_get
#
# An HTTP GET request with basic error handling.
#
# Inputs:
#   url: The URL to request.
#
# Outputs:
#   The content of the HTTP response.
###############################################################################
def simple_get(url):
  try:
    response = get(url)
    content_type = response.headers['Content-Type'].lower()
    if (response.status_code == 200 and content_type is not None and content_type.find('html') > -1):
      return response.content
    else:
      print(f"wtf: {response}")
  except RequestException as e:
    print(f"Error during GET to {url}: {str(e)}", flush=True)

def broken_urls():
  return [
    "https://www.hockey-reference.com/boxscores/201401070BUF.html", # Postponed for blizzard
    "https://www.hockey-reference.com/boxscores/201401210PHI.html", # Postponed for blizzard
    "https://www.hockey-reference.com/boxscores/201401240CAR.html", # Postponed for blizzard make-up game
    "https://www.hockey-reference.com/boxscores/201403100DAL.html"  # Rick Peverley medical emergency
  ]


def stringy_now():
  return time.asctime(time.localtime())

###############################################################################
if __name__ == "__main__":
  main()

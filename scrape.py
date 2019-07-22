from requests import get
from requests.exceptions import RequestException
from os import path

import csv
import time

import constants
import extract
import teams

def main():
  print(f"{stringy_now()}: Started scraping", flush=True)
  start = time.time()
  base_url = "https://www.hockey-reference.com"

  years = range(constants.FIRST_YEAR, constants.PRESENT_YEAR + 1)
  for year in years:
    regular_season_serialized_games = []
    regular_season_filename = f"data/{year}.csv"
    # This is expensive, so we don't want to do it if we already have the data.
    if path.isfile(regular_season_filename):
      print(f"{regular_season_filename} already exists, skipping")
    else:
      regular_season_serialized_games = scrape_regular_season(year, base_url)
      write_file(regular_season_serialized_games, regular_season_filename)

    playoff_serialized_games = []
    playoff_filename = f"data/{year}_playoffs.csv"
    # Still expensive when there's less games
    if path.isfile(playoff_filename):
      print(f"{playoff_filename} already exists, skipping")
    else:
      playoff_serialized_games = scrape_playoffs(year, base_url)
      write_file(playoff_serialized_games, playoff_filename)

  end = time.time()
  print(f"Total time: {end-start}", flush=True)

###############################################################################
# scrape_regular_season
#
# Scrapes hockey-reference for regular season game data for a given year.
#
# Inputs:
#   year: The year for which to get regular season data.
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
def scrape_regular_season(year, base_url):
    serialized_games = []
    active_teams_by_abbr = {abbr: team for abbr, team in teams.teams_by_abbr().items() if team.stint_by_year(year) is not None}
    urls_by_team = {team: f"{base_url}/teams/{team.stint_by_year(year).abbr}/{year}_gamelog.html" for abbr, team in active_teams_by_abbr.items()}
    for team, url in urls_by_team.items():
      print(f"{stringy_now()}: Scraping {team.stint_by_year(year).abbr} games from {year}", flush=True)
      game_urls = extract.get_game_urls_from_gamelog(simple_get(url).content, base_url)
      for game_url in game_urls:
        print(f"{stringy_now()}: Scraping {game_url}", flush=True)
        game_html = simple_get(game_url).content
        (winner, loser, num_penalties) = extract.get_penalties_from_game(game_html, year)
        serialized_games.append((winner, loser, num_penalties, game_url))
    # Dedupe.
    return set(serialized_games)

###############################################################################
# scrape_playoffs
#
# Scrapes hockey-reference for playoff game data for a given year
#
# Inputs:
#   year: The year for which to get playoff data
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
def scrape_playoffs(year, base_url):
  serialized_games = []
  print(f"{stringy_now()}: Scraping playoff games from {year}", flush=True)
  playoff_url = f"{base_url}/playoffs/NHL_{year}.html"
  playoffs_html = simple_get(playoff_url).content
  series_urls = extract.get_series_urls_from_playoffs_summary(playoffs_html, base_url)
  for series_url in series_urls:
    print(f"{stringy_now()}: Scraping {series_url}", flush=True)
    series_html = simple_get(series_url).content
    game_urls = extract.get_game_urls_from_series(series_html, base_url)
    for game_url in game_urls:
      print(f"{stringy_now()}: Scraping {game_url}", flush=True)
      game_html = simple_get(game_url).content
      (winner, loser, num_penalties) = extract.get_penalties_from_game(game_html, year)
      serialized_games.append((winner, loser, num_penalties, game_url))
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
  with open(filename, 'w', newline="") as file:
    writer = csv.writer(file, delimiter=",")
    writer.writerow(["game_id", "winner", "loser", "num_penalties"])
    for (winner, loser, num_penalties, game_url) in serialized_games:
      game_id = game_url.split("/")[-1].split(".")[0]
      writer.writerow([game_id,winner,loser,num_penalties])

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
      return response
    else:
      print(f"wtf: {response}")
  except RequestException as e:
    print(f"Error during GET to {url}: {str(e)}", flush=True)

def stringy_now():
  return time.asctime(time.localtime())

###############################################################################
if __name__ == "__main__":
  main()

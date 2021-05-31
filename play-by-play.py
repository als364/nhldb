#!/usr/bin/env python3

from requests import get

import json
import os
import time

from penalty import Penalty
from season import Season

import constants

def main():
  print(f"{stringy_now()}: Started scraping", flush=True)
  start = time.time()
  years = [year for year in range(constants.FIRST_YEAR, constants.PRESENT_YEAR + 1) if year not in constants.BROKEN_YEARS]
  for year in years:
    season = Season(year)
    maybe_make_directory(season)

    print("Getting schedule")
    schedule = get(f"https://statsapi.web.nhl.com/api/v1/schedule?season={season.season_id()}").json()

    response = get_pbp_data(2018020778)
    with open("cruft/response.json", "w") as outfile:
      json.dump(response, outfile)

    regular_game_ids = []
    playoff_game_ids = []
    print("Organizing dates")
    dates = schedule["dates"]
    for date in dates:
      games = date["games"]
      for game in games:
        if game["gameType"] == "R":
          regular_game_ids.append(game["gamePk"])
        elif game["gameType"] == "P":
          playoff_game_ids.append(game["gamePk"])

    for regular_game_id in regular_game_ids:
      regular_game_filename = f"penalty_data/{season.season_id()}/{regular_game_id}.txt"
      if os.path.isfile(regular_game_filename):
        print(f"Skipping: {regular_game_id}")
      else:
        print(f"Getting game: {regular_game_id}")
        pbp_data = get_pbp_data(regular_game_id)
        penalties = get_penalties(pbp_data)
        seralized_penalties = [str(penalty) for penalty in penalties]
        write_file(seralized_penalties, regular_game_filename)

    for playoff_game_id in playoff_game_ids:
      playoff_game_filename = f"penalty_data/{season.season_id()}/{playoff_game_id}.txt"
      if os.path.isfile(playoff_game_filename):
        print(f"Skipping: {playoff_game_id}")
      else:
        print(f"Getting game: {playoff_game_id}")
        pbp_data = get_pbp_data(playoff_game_id)
        penalties = get_penalties(pbp_data)
        seralized_penalties = [str(penalty) for penalty in penalties]
        write_file(seralized_penalties, playoff_game_filename)

  end = time.time()
  print(f"Total time: {end-start}", flush=True)

def get_pbp_data(game_id):
  try:
    response = get(f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live")
    content_type = response.headers['Content-Type'].lower()
    if (response.status_code == 200 and content_type is not None and content_type.find('json') > -1):
      with open("cruft/response.json", "w") as file:
        json.dump(response.json(), file)
      return response.json()
    else:
      print(f"wtf: {response}")
  except RequestException as e:
    print(f"Error during GET to {url}: {str(e)}", flush=True)

def get_penalties(pbp_data):
  plays = pbp_data["liveData"]["plays"]["allPlays"]
  penalties_json = [play for play in plays if play["result"] and play["result"]["eventTypeId"] == "PENALTY"]

  penalties = []
  for penalty_json in penalties_json:
    players = penalty_json["players"]
    penalty_on = [player["player"]["fullName"] for player in players if player["playerType"] == "PenaltyOn"][0]
    # the nhl remains unaware of the past perfect
    drawn_by_array = [player["player"]["fullName"] for player in players if player["playerType"] == "DrewBy"]
    # bench minors, unsportsmanlike conduct, etc. don't have a drawn by so we gotta be careful
    drawn_by = drawn_by_array[0] if drawn_by_array else None

    result = penalty_json["result"]
    about = penalty_json["about"]

    penalty = Penalty(
      penalty_on, 
      drawn_by, 
      result["secondaryType"], 
      result["penaltySeverity"], 
      result["penaltyMinutes"], 
      penalty_json["team"]["name"],
      about["period"],
      about["periodTime"]
    )
    penalties.append(penalty)
  return penalties

def write_file(seralized_penalties, filename):
  with open(filename, 'w') as file:
    for line in seralized_penalties:
      file.write(f"{line}\n")

def maybe_make_directory(season):
  if(not os.path.exists(f"penalty_data/{season.season_id()}")):
    os.mkdir(f"penalty_data/{season.season_id()}")

def stringy_now():
  return time.asctime(time.localtime())

###############################################################################
if __name__ == "__main__":
  main()
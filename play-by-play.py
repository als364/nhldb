#!/usr/bin/env python3
from functools import partial

from requests import get, RequestException

import json
import os
import time

from penalty import Penalty
from season import Season

import constants


def main():
    print(f"{stringy_now()}: Started scraping", flush=True)
    start = time.time()
    years = [year for year in range(constants.FIRST_YEAR, constants.PRESENT_YEAR + 1) if
             year not in constants.BROKEN_YEARS]
    for year in years:
        season = Season(year)
        maybe_make_directory(season)

        print("Getting schedule")
        schedule = get(f"https://statsapi.web.nhl.com/api/v1/schedule?season={season.season_id()}").json()

        response = get_pbp_data(2018020778)
        with open("response.json", "w") as outfile:
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

        # write_per_game_files(season, regular_game_ids, playoff_game_ids)
        write_per_season_csvs(season, regular_game_ids, playoff_game_ids)

    end = time.time()
    print(f"Total time: {end - start}", flush=True)


def get_pbp_data(game_id):
    url = f"https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live"
    try:
        response = get(url)
        content_type = response.headers['Content-Type'].lower()
        if response.status_code == 200 and content_type is not None and content_type.find('json') > -1:
            with open("response.json", "w") as file:
                json.dump(response.json(), file)
            return response.json()
        else:
            print(f"wtf: {response}")
    except RequestException as e:
        print(f"Error during GET to {url}: {str(e)}", flush=True)


def get_game_context(pbp_data):
    home_team = pbp_data["gameData"]["teams"]["home"]["name"]
    away_team = pbp_data["gameData"]["teams"]["away"]["name"]
    return home_team, away_team


def write_per_game_files(season, regular_game_ids, playoff_game_ids):
    def get_game_penalties(game_id):
        pbp_data = get_pbp_data(regular_game_id)
        penalties = get_penalties(pbp_data, get_penalty_model)
        return [str(penalty) for penalty in penalties]

    for regular_game_id in regular_game_ids:
        regular_game_filename = f"penalty_data/{season.season_id()}/{regular_game_id}.txt"
        if os.path.isfile(regular_game_filename):
            print(f"Skipping: {regular_game_id}")
        else:
            print(f"Getting regular season game: {regular_game_id}")
            serialized_penalties = get_game_penalties(regular_game_id)
            write_file(serialized_penalties, regular_game_filename)

    for playoff_game_id in playoff_game_ids:
        playoff_game_filename = f"penalty_data/{season.season_id()}/{playoff_game_id}.txt"
        if os.path.isfile(playoff_game_filename):
            print(f"Skipping: {playoff_game_id}")
        else:
            print(f"Getting playoff game: {playoff_game_id}")
            serialized_penalties = get_game_penalties(playoff_game_id)
            write_file(serialized_penalties, playoff_game_filename)


def write_per_season_csvs(season, regular_game_ids, playoff_game_ids):
    def get_game_penalties(game_id):
        pbp_data = get_pbp_data(game_id)
        home_team, away_team = get_game_context(pbp_data)
        return get_penalties(pbp_data, partial(get_normalized_penalty_dict, home_team=home_team, away_team=away_team))

    season_id = season.season_id()
    with open(f"penalty_data/{season_id}/{season_id}_regular_season_penalties.csv", "w") as regular_file:
        regular_file.write(
            "PenalizedPlayerId,PenalizedPlayerName,DrawnByPlayerId,DrawnByPlayerName,PenaltyType,PenaltySeverity,PenaltyMinutes,Period,PeriodTime,HomeTeam,AwayTeam,HomeTeamGoals,AwayTeamGoals,XCoord,YCoord\n")
        for index, regular_game_id in enumerate(regular_game_ids):
            print(f"Getting regular season game {index} of {len(regular_game_ids)} ({round((index / len(regular_game_ids)) * 100, 2)}%)")
            for penalty in get_game_penalties(regular_game_id):
                regular_file.write(get_penalty_csv_line(penalty))

    with open(f"penalty_data/{season.season_id()}/{season.season_id()}_playoff_penalties.csv", "w") as playoff_file:
        for index, playoff_game_id in enumerate(playoff_game_ids):
            print(f"Getting playoff game {index} of {len(playoff_game_ids)} ({round((index / len(playoff_game_ids)) * 100, 2)}%)")
            for penalty in get_game_penalties(playoff_game_id):
                playoff_file.write(get_penalty_csv_line(penalty))


def get_penalties(pbp_data, penalty_json_handler):
    plays = pbp_data["liveData"]["plays"]["allPlays"]
    penalties_json = [play for play in plays if play["result"] and play["result"]["eventTypeId"] == "PENALTY"]

    penalties = []
    for penalty_json in penalties_json:
        penalty = penalty_json_handler(penalty_json)
        penalties.append(penalty)
    return penalties


def get_normalized_penalty_dict(penalty_json, home_team, away_team):
    players = penalty_json["players"]
    penalty_on = [player["player"] for player in players if player["playerType"] == "PenaltyOn"][0]
    # the nhl remains unaware of the past perfect
    drawn_by_array = [player["player"] for player in players if player["playerType"] == "DrewBy"]
    # bench minors, unsportsmanlike conduct, etc. don't have a drawn by
    drawn_by = drawn_by_array[0] if drawn_by_array else None

    result = penalty_json["result"]
    about = penalty_json["about"]
    coordinates = penalty_json["coordinates"]

    return {
        "PenalizedPlayerId": penalty_on["id"],
        "PenalizedPlayerName": penalty_on["fullName"],
        "DrawnByPlayerId": drawn_by["id"] if drawn_by is not None else '',
        "DrawnByPlayerName": drawn_by["fullName"] if drawn_by is not None else '',
        "PenaltyType": result["secondaryType"],
        "PenaltySeverity": result["penaltySeverity"],
        "PenaltyMinutes": result["penaltyMinutes"],
        "Period": about["period"],
        "PeriodTime": about["periodTime"],
        "HomeTeam": home_team,
        "AwayTeam": away_team,
        "HomeTeamGoals": about["goals"]["home"],
        "AwayTeamGoals": about["goals"]["away"],
        "XCoord": coordinates["x"],
        "YCoord": coordinates["y"],
    }


def get_penalty_csv_line(normalized_penalty_dict):
    return f"{normalized_penalty_dict['PenalizedPlayerId']},{normalized_penalty_dict['PenalizedPlayerName']},{normalized_penalty_dict['DrawnByPlayerId']},{normalized_penalty_dict['DrawnByPlayerName']},{normalized_penalty_dict['PenaltyType']},{normalized_penalty_dict['PenaltySeverity']},{normalized_penalty_dict['PenaltyMinutes']},{normalized_penalty_dict['Period']},{normalized_penalty_dict['PeriodTime']},{normalized_penalty_dict['HomeTeam']},{normalized_penalty_dict['AwayTeam']},{normalized_penalty_dict['HomeTeamGoals']},{normalized_penalty_dict['AwayTeamGoals']},{normalized_penalty_dict['XCoord']},{normalized_penalty_dict['YCoord']}\n"


def get_penalty_model(penalty_json):
    players = penalty_json["players"]
    penalty_on = [player["player"]["fullName"] for player in players if player["playerType"] == "PenaltyOn"][0]
    # the nhl remains unaware of the past perfect
    drawn_by_array = [player["player"]["fullName"] for player in players if player["playerType"] == "DrewBy"]
    # bench minors, unsportsmanlike conduct, etc. don't have a drawn by so we gotta be careful
    drawn_by = drawn_by_array[0] if drawn_by_array else None

    result = penalty_json["result"]
    about = penalty_json["about"]

    return Penalty(
        penalty_on,
        drawn_by,
        result["secondaryType"],
        result["penaltySeverity"],
        result["penaltyMinutes"],
        penalty_json["team"]["name"],
        about["period"],
        about["periodTime"]
    )


def write_file(seralized_penalties, filename):
    with open(filename, 'w') as file:
        for line in seralized_penalties:
            file.write(f"{line}\n")


def maybe_make_directory(season):
    if (not os.path.exists(f"penalty_data/{season.season_id()}")):
        os.mkdir(f"penalty_data/{season.season_id()}")


def stringy_now():
    return time.asctime(time.localtime())


###############################################################################
if __name__ == "__main__":
    main()

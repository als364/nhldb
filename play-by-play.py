#!/usr/bin/env python3

from requests import get

import json

from penalty import Penalty

def main():
	pbp_data = get_pbp_data()
	penalties = get_penalties(pbp_data)

	for penalty_json in penalties:
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

def get_pbp_data():
	return get("https://statsapi.web.nhl.com/api/v1/game/2019020849/feed/live").json()

def get_penalties(pbp_data):
	plays = pbp_data["liveData"]["plays"]["allPlays"]
	penalties = [play for play in plays if play["result"] and play["result"]["eventTypeId"] == "PENALTY"]
	return penalties

###############################################################################
if __name__ == "__main__":
  main()
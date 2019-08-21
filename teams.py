import json

import constants
from team import Team
from team_stint import Team_Stint

###############################################################################
# extract
#
# Recursively munges data from a json with team data into a data structure.
#
# Inputs:
#   path: The path for the file.
#
# Outputs:
#   A map of abbr: Team objects for all teams, current and defunct. Current
#   Team's in the map contain all Team_Stint's in their history; defunct Team's
#   contain all Team_Stint's prior to their relocation or renaming.
###############################################################################
def extract(path):
  with open(path) as file:
    teams_json = json.load(file)
    teams = {}
    for team_json in teams_json:
      abbr = team_json["abbr"]
      teams[abbr] = Team(
        abbr,
        team_json["name"],
        team_json["start"],
        team_json["conference"],
        team_json["division"],
        []
      )
      if "previous" in team_json:
        previous_json = team_json["previous"]
        for previous_stint in previous_json:
          stint = Team_Stint(
            previous_stint["abbr"],
            previous_stint["name"],
            previous_stint["start"],
            previous_stint["end"]
          )
          teams[abbr].previous.append(stint)

    return teams

def _include_defunct(teams, defunct_teams, include_defunct):
  if len(defunct_teams) is 0:
    return teams
  else:
    for stint in defunct_teams.values():
      if stint.next_abbr in teams:
        teams[stint.next_abbr].stints.append(stint)
      teams[stint.abbr] = Team(stint.abbr, stint.name, [stint])
    remaining_stints = [stint for stint in stints if stint.abbr not in teams.keys()]
    return _extract(teams, remaining_stints)

def _collapse_defunct_teams(stints):
  remaining_stints = [stint for stint in stints if stint.next_abbr in stints.key()]
  if len(remaining_stints) == 0:
    return stints
  for abbr, stint in stints.items():
    if stint.next_abbr in stints.keys():
      stints[stint.next_abbr].stints.append(stint)
  return collapse_defunct_teams(stints)

# Lazy static eval
teams = extract("data/teams.json")

def teams_by_abbr():
  return teams

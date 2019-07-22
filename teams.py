import csv

import constants
from team import Team
from team_stint import Team_Stint

###############################################################################
# extract_data_from_csv
#
# Recursively munges data from a csv with team data into a data structure.
#
# Inputs:
#   path: The path for the file.
#
# Outputs:
#   A map of abbr: Team objects for all teams, current and defunct. Current
#   Team's in the map contain all Team_Stint's in their history; defunct Team's
#   contain all Team_Stint's prior to their relocation or renaming.
###############################################################################
def extract_data_from_csv(path):
  with open(path) as file:
    reader = csv.DictReader(file, delimiter=",")
    team_stints = [
      Team_Stint(
        stint["abbr"],
        stint["name"],
        int(stint["start"]),
        constants.PRESENT_YEAR if stint["end"] == constants.PRESENT_STRING else int(stint["end"]),
        None if stint["next"] == "" else stint["next"],
        None if stint["prev"] == "" else stint["prev"]
      )
      for stint in reader
    ]
    teams = {stint.abbr: Team(stint.abbr, stint.name, [stint]) for stint in team_stints if stint.next_abbr is None}
    defunct_teams = [stint for stint in team_stints if stint.next_abbr is not None]
    return _extract_data_from_csv(teams, defunct_teams)

def _extract_data_from_csv(teams, stints):
  if len(stints) is 0:
    return teams
  else:
    for stint in stints:
      if stint.next_abbr in teams:
        teams[stint.next_abbr].stints.append(stint)
      teams[stint.abbr] = Team(stint.abbr, stint.name, [stint])
    remaining_stints = [stint for stint in stints if stint.abbr not in teams.keys()]
    return _extract_data_from_csv(teams, remaining_stints)

# Lazy static eval
present_teams = extract_data_from_csv("data/stints.csv")

def teams_by_abbr():
  return present_teams

def teams_by_name():
  return {team.name: team for abbr, team in present_teams.items()}

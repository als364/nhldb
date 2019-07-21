import csv

import constants
from team import Team
from team_stint import Team_Stint

def extract_data_from_csv(path):
  with open(path) as file:
    reader = csv.DictReader(file, delimiter=",")
    team_stints = [
      Team_Stint(
        stint["abbr"],
        stint["name"],
        int(stint["start"]),
        constants.PRESENT_YEAR if stint["end"] == constants.PRESENT_STRING else int(stint["end"]),
        None if stint["next"] == "" else stint["next"]
      )
      for stint in reader
    ]
    present_teams = {stint.abbr: Team(stint.abbr, stint.name, [stint]) for stint in team_stints if stint.next_abbr is None}
    remaining_teams = [stint for stint in team_stints if stint.next_abbr is not None]
    return _extract_data_from_csv(present_teams, remaining_teams)

def _extract_data_from_csv(present_teams_by_abbr, remaining_team_stints):
  if len(remaining_team_stints) is 0:
    return present_teams_by_abbr
  else:
    for remaining_team_stint in remaining_team_stints:
      for present_team_abbr, present_team in present_teams_by_abbr.items():
        all_team_abbrs = [present_team_stint.abbr for present_team_stint in present_team.stints]
        if (remaining_team_stint.next_abbr is present_team_abbr or remaining_team_stint.next_abbr in all_team_abbrs):
          present_team.stints.append(remaining_team_stint)
          remaining_team_stints.remove(remaining_team_stint)
    return _extract_data_from_csv(present_teams_by_abbr, remaining_team_stints)

# Lazy static eval
present_teams = extract_data_from_csv("data/stints.csv")

def teams_by_abbr():
  return present_teams

def teams_by_name():
  return {team.name: team for abbr, team in present_teams.items()}

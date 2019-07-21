import csv

import constants
from team import Team
from team_stint import Team_Stint

#Current NHL teams
team_name_by_abbr = {
  "ANA": "Anaheim Ducks",
  "ARI": "Arizona Coyotes",
  "ATF": "Atlanta Flames",
  "ATL": "Atlanta Thrashers",
  "BOS": "Boston Bruins",
  "BUF": "Buffalo Sabres",
  "CGY": "Calgary Flames",
  "CAR": "Carolina Hurricanes",
  "CHI": "Chicago Blackhawks",
  "COL": "Colorado Avalanche",
  "CLR": "Colorado Rockies",
  "CBJ": "Columbus Blue Jackets",
  "DAL": "Dallas Stars",
  "DET": "Detroit Red Wings",
  "EDM": "Edmonton Oilers",
  "FLA": "Florida Panthers",
  "HAR": "Hartford Whalers",
  "KCS": "Kansas City Scouts",
  "LAK": "Los Angeles Kings",
  "MDA": "Mighty Ducks of Anaheim",
  "MNS": "Minnesota North Stars",
  "MIN": "Minnesota Wild",
  "MTL": "Montreal Canadiens",
  "NSH": "Nashville Predators",
  "NJD": "New Jersey Devils",
  "NYI": "New York Islanders",
  "NYR": "New York Rangers",
  "OTT": "Ottawa Senators",
  "QUE": "Quebec Nordiques",
  "PHI": "Philadelphia Flyers",
  "PHX": "Phoenix Coyotes",
  "PIT": "Pittsburgh Penguins",
  "SJS": "San Jose Sharks",
  "STL": "St. Louis Blues",
  "TBL": "Tampa Bay Lightning",
  "TRA": "Toronto Arenas",
  "TOR": "Toronto Maple Leafs",
  "TRS": "Toronto St. Patricks",
  "VAN": "Vancouver Canucks",
  "VEG": "Vegas Golden Knights",
  "WSH": "Washington Capitals",
  "WPG": "Winnipeg Jets",
  "WIN": "Winnipeg Jets"
}

team_abbrs_by_name = {
  "Anaheim Ducks": ["ANA"],
  "Arizona Coyotes": ["ARI"],
  "Atlanta Flames": ["ATF"],
  "Atlanta Thrashers": ["ATL"],
  "Boston Bruins": ["BOS"],
  "Buffalo Sabres": ["BUF"],
  "Calgary Flames": ["CGY"],
  "Carolina Hurricanes": ["CAR"],
  "Chicago Blackhawks": ["CHI"],
  "Colorado Avalanche": ["COL"],
  "Colorado Rockies": ["CLR"],
  "Columbus Blue Jackets": ["CBJ"],
  "Dallas Stars": ["DAL"],
  "Detroit Red Wings": ["DET"],
  "Edmonton Oilers": ["EDM"],
  "Florida Panthers": ["FLA"],
  "Hartford Whalers": ["HAR"],
  "Kansas City Scouts": ["KCS"],
  "Los Angeles Kings": ["LAK"],
  "Mighty Ducks of Anaheim": ["MDA"],
  "Minnesota North Stars": ["MNS"],
  "Minnesota Wild": ["MIN"],
  "Montreal Canadiens": ["MTL"],
  "Nashville Predators": ["NSH"],
  "New Jersey Devils": ["NJD"],
  "New York Islanders": ["NYI"],
  "New York Rangers": ["NYR"],
  "Ottawa Senators": ["OTT"],
  "Quebec Nordiques": ["QUE"],
  "Philadelphia Flyers": ["PHI"],
  "Phoenix Coyotes": ["PHX"],
  "Pittsburgh Penguins": ["PIT"],
  "San Jose Sharks": ["SJS"],
  "St. Louis Blues": ["STL"],
  "Tampa Bay Lightning": ["TBL"],
  "Toronto Arenas": ["TRA"],
  "Toronto Maple Leafs": ["TOR"],
  "Toronto St. Patricks": ["TRS"],
  "Vancouver Canucks": ["VAN"],
  "Vegas Golden Knights": ["VEG"],
  "Washington Capitals": ["WSH"],
  "Winnipeg Jets": ["WPG", "WIN"]
}

historical_names_by_abbr = {
  "ANA": ["Anaheim Ducks", "Mighty Ducks of Anaheim"],
  "ARI": ["Arizona Coyotes", "Phoenix Coyotes", "Winnipeg Jets"],
  "BOS": ["Boston Bruins"],
  "BUF": ["Buffalo Sabres"],
  "CGY": ["Calgary Flames", "Atlanta Flames"],
  "CAR": ["Carolina Hurricanes", "Hartford Whalers"],
  "CHI": ["Chicago Blackhawks", "Chicago Black Hawks"],
  "COL": ["Colorado Avalanche", "Quebec Nordiques"],
  "CBJ": ["Columbus Blue Jackets"],
  "DAL": ["Dallas Stars", "Minnesota North Stars"],
  "DET": ["Detroit Red Wings", "Detroit Falcons", "Detroit Cougars"],
  "EDM": ["Edmonton Oilers"],
  "FLA": ["Florida Panthers"],
  "LAK": ["Los Angeles Kings"],
  "MIN": ["Minnesota Wild"],
  "MTL": ["Montreal Canadiens"],
  "NSH": ["Nashville Predators"],
  "NJD": ["New Jersey Devils", "Colorado Rockies", "Kansas City Scouts"],
  "NYI": ["New York Islanders"],
  "NYR": ["New York Rangers"],
  "OTT": ["Ottawa Senators"],
  "PHI": ["Philadelphia Flyers"],
  "PIT": ["Pittsburgh Penguins"],
  "SJS": ["San Jose Sharks"],
  "STL": ["St. Louis Blues"],
  "TBL": ["Tampa Bay Lightning"],
  "TOR": ["Toronto Maple Leafs", "Toronto St. Patricks", "Toronto Arenas"],
  "VAN": ["Vancouver Canucks"],
  "VEG": ["Vegas Golden Knights"],
  "WSH": ["Washington Capitals"],
  "WPG": ["Winnipeg Jets", "Atlanta Thrashers"]
}

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
  return {team.name: team for team in present_teams}

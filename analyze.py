import argparse
import os

from functools import reduce

import constants
import teams

def main():
  args = parse()
  team = args.team
  other_teams = args.other_teams

  games = {abbr: [] for abbr in other_teams}
  years = [year for year in range(2015, constants.PRESENT_YEAR + 1) if year not in constants.BROKEN_YEARS]
  for year in years:
    with open(f"data/{year}/{team}.csv") as file:
      regular_season_games = munge(team, other_teams, file.readlines())
      games = merge(games, regular_season_games)
    playoff_filename = f"data/{year}/{team}_playoffs.csv"
    if args.include_playoffs and os.path.isfile(playoff_filename):
      with open(playoff_filename) as file:
        playoff_games = munge(team, other_teams, file.readlines())
        games = games.merge(games, regular_season_games)
        
  if len(other_teams) > 0:
    for other_team in other_teams:
      p_win_fight = calc_win_given_fight(games[other_team], team)
      print(f"The conditional probability of {team} winning a {other_team} game with a fight is {p_win_fight}")
      p_win_no_fight = calc_win_given_no_fight(games[other_team], team)
      print(f"The conditional probability of {team} winning a {other_team} game without a fight is {p_win_no_fight}")
  else:
    all_games = []
    for abbr, games_list in games.items():
      all_games.extend(games_list)
    p_win_fight = calc_win_given_fight(all_games, team)
    print(f"The conditional probability of {team} winning a game with a fight is {p_win_fight}")
    p_win_no_fight = calc_win_given_no_fight(all_games, team)
    print(f"The conditional probability of {team} winning a game without a fight is {p_win_no_fight}")

###############################################################################
# munge
#
# Munges data from a csv with game data into a data structure.
#
# Inputs:
#   team: The abbr of the team we're calculating win probablity for.
#   other_teams: A list of teams to compare against.
#   csvlines: A list of serialized game data.
#
# Outputs:
#   A dict of lists of dicts of other team abbr to games played between the
#   teams.
###############################################################################
def munge(team, other_teams, csvlines):
  year_games = [line.split(",") for line in csvlines]
  team_games = [year_game for year_game in year_games if year_game[1] == team or year_game[2] == team]
  if len(other_teams) > 0:
    team_games = [team_game for team_game in team_games if team_game[1] in other_teams or team_game[2] in other_teams]
  games = {abbr: [] for abbr in other_teams}
  for team_game in team_games:
    team_game_map = {
      "game_id": team_game[0],
      "winner": team_game[1],
      "loser": team_game[2],
      "num_penalties": int(team_game[3])
    }
    if team_game_map["winner"] == team:
      if team_game_map["loser"] in games:
        games[team_game_map["loser"]].append(team_game_map)
      else:
        games[team_game_map["loser"]] = [team_game_map]
    else:
      if team_game_map["winner"] in games:
        games[team_game_map["winner"]].append(team_game_map)
      else:
        games[team_game_map["winner"]] = [team_game_map]
  return games

###############################################################################
# merge
#
# Munges data from a csv with game data into a data structure.
#
# Inputs:
#   games: A dict of lists of dicts of games
#   new_games: A dict of lists of dicts of games to merge into the first dict
#
# Outputs:
#   A dict consisting of all the values of new_games appended onto all the
#   values of games.
###############################################################################
def merge(games, new_games):
  for abbr, new_games_list in new_games.items():
    if abbr in games:
      games[abbr].extend(new_games_list)
    else:
      games[abbr] = new_games_list
  return games

###############################################################################
# calc_win_given_fight
#
# Inputs:
#   games: A list of game data maps.
#   winner: The team for which to calculate P(win|fight).
#
# Outputs:
#   The conditional probability that the winner wins a game, given a fight
###############################################################################
def calc_win_given_fight(games, winner):
  count = len(games)
  games_with_fight = len([game for game in games if game["num_penalties"] > 0])
  games_with_win_and_fight = len([game for game in games if game["winner"] == winner and game["num_penalties"] > 0])
  p_win_and_fight = games_with_win_and_fight / count
  p_fight = games_with_fight / count
  return p_win_and_fight / p_fight

###############################################################################
# calc_win_given_no_fight
#
# Inputs:
#   games: A list of game data maps.
#   winner: The team for which to calculate P(win|no fight).
#
# Outputs:
#   The conditional probability that the winner wins a game, given no fight
###############################################################################
def calc_win_given_no_fight(games, winner):
  count = len(games)
  games_without_fight = len([game for game in games if game["num_penalties"] == 0])
  games_without_win_and_fight = len([game for game in games if game["winner"] == winner and game["num_penalties"] == 0])
  p_win_and_fight = games_without_win_and_fight / count
  p_fight = games_without_fight / count
  return p_win_and_fight / p_fight

def parse():
  parser = argparse.ArgumentParser(description="Gets the conditional probability"
    + "of a team or teams (head-to-head) winning games with or without a fight")
  parser.add_argument(
    "-t",
    "--team",
    choices=teams.teams_by_abbr().keys(),
    help="The three-letter abbreviation of a team to compare",
    required=True
  )
  parser.add_argument(
    "-o",
    "--other-teams",
    choices=teams.teams_by_abbr().keys(),
    nargs='*',
    help="The three-letter abbreviations of one or more teams to compare " +
      "against. If none are provided, all games by the first team will be " +
      "analyzed.",
    default=[]
  )
  parser.add_argument(
    "-i",
    "--include-playoffs",
    action="store_true",
    default=False,
    help="Whether or not to include playoff data. Default: False"
  )
  return parser.parse_args()

###############################################################################
if __name__ == "__main__":
  main()
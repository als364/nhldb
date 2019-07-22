import argparse

import constants
import teams

def main():
  args = parse()
  teams = args.teams

  years = range(constants.FIRST_YEAR, constants.PRESENT_YEAR + 1)
  games = []
  for year in years:
    with open(f"data/{year}.csv") as file:
      games.extend(munge(teams, file.readlines()))
    if args.include_playoffs:
      with open(f"data/{year}_playoffs.csv") as file:
        games.extend(munge(teams, file.readlines()))

  p_win_fight = calc_win_given_fight(games, teams[0])
  print(f"The conditional probability of {teams[0]} winning a game with a fight is {p_win_fight}")
  p_win_no_fight = calc_win_given_no_fight(games, teams[0])
  print(f"The conditional probability of {teams[0]} winning a game without a fight is {p_win_no_fight}")

###############################################################################
# munge
#
# Munges data from a csv with game data into a data structure.
#
# Inputs:
#   teams: A tuple of team abbrs to pull data for.
#   csvlines: A list of serialized game data.
#
# Outputs:
#   A list of maps of games played between the two teams.
###############################################################################
def munge(teams, csvlines):
  year_games = [line.split(",") for line in csvlines]
  team_games = [year_game for year_game in year_games if year_game[1] in teams and year_game[2] in teams]
  games = []
  for team_game in team_games:
    team_game_map = {
      "game_id": team_game[0],
      "winner": team_game[1],
      "loser": team_game[2],
      "num_penalties": int(team_game[3])
    }
    games.append(team_game_map)
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
    + "of one team winning against another team with and without a fight"
    + "in the game")
  parser.add_argument(
    "teams",
    metavar="T",
    choices=teams.teams_by_abbr().keys(),
    nargs=2,
    help="The three-letter abbreviations of the two teams to compare"
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
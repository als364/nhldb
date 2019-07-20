import argparse

import teams


def main():
  teams = parse().teams
  
  # years = range(2019, 2020)
  years = [20172019]
  games = []
  for year in years:
    with open(f"data/{year}.csv") as file:
      year_games = [line.split(",") for line in file.readlines()]
      team_games = [year_game for year_game in year_games if year_game[1] in teams and year_game[2] in teams]
      for team_game in team_games:
        team_game_map = {
          "game_id": team_game[0],
          "winner": team_game[1],
          "loser": team_game[2],
          "num_penalties": int(team_game[3])
        }
        games.append(team_game_map)

  p_team_1 = conditional_probability(games, teams[0])
  print(f"The conditional probability of {teams[0]} winning a game with a fight is {p_team_1}")
  p_team_2 = conditional_probability(games, teams[1])
  print(f"The conditional probability of {teams[1]} winning a game with a fight is {p_team_2}")

def conditional_probability(games, winner):
  count = len(games)
  games_with_fight = len([game for game in games if game["num_penalties"] > 0])
  games_with_win_and_fight = len([game for game in games if game["winner"] == winner and game["num_penalties"] > 0])
  p_win_and_fight = games_with_win_and_fight / count
  p_fight = games_with_fight / count
  return p_win_and_fight / p_fight

def parse():
  parser = argparse.ArgumentParser(description="Gets the conditional probability"
    + "of one team winning against another team with and without a fight"
    + "in the game")
  parser.add_argument(
    'teams',
    metavar="T",
    choices=teams.team_name_by_abbr.keys(),
    nargs=2,
    help="The three-letter abbreviations of the two teams to compare"
  )
  return parser.parse_args()

###############################################################################
if __name__ == "__main__":
  main()
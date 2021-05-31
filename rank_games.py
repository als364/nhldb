#!/usr/bin/env python3

"""nhl-rank.py: An utility to rank games by a team in a certain year without revealing the results.
   The data source and its copyright: https://sportsdatabase.com/
"""

__author__ = "Lex Vorona"


import sys, getopt
import requests
import json
from datetime import datetime

weights = {
    'goal': 100.0,
    'shot': 10.0,
    'chance': 20.0,
    'powerplay': -5.0,
    'shorthand': 50.0,
    'penalty': 1000.0,
}

winner = 1.0

def rank(game):
    score = 0.0;
    if not game['goals'] is None:
        score = score + int(game['goals']) * weights['goal'] * winner
    if not game['opp_goals'] is None:
        score = score + int(game['opp_goals']) * weights['goal']
    if not game['shots'] is None:
        score = score + int(game['shots']) * weights['shot'] * winner
    if not game['shots_against'] is None:
        score = score + int(game['shots_against']) * weights['shot']
    # score = score + int(game['chances_pp']) * weights['chance'] * winner
    # score = score + int(game['opp_chances_pp']) * weights['chance']
    # score = score + int(game['goals_pp']) * weights['powerplay'] * winner
    # score = score + int(game['goals_against_pp']) * weights['powerplay']
    # score = score + int(game['goals_sh']) * weights['shorthand'] * winner
    # score = score + int(game['goals_against_sh']) * weights['shorthand']
    if not game['pen_min'] is None:
        score = score + int(game['pen_min']) * weights['penalty']
    if not game['pen_min_opp'] is None:
        score = score + int(game['pen_min_opp']) * weights['penalty']
    return score

def rank_games(team, year):
    url = 'https://api.sportsdatabase.com/nhl/query.json?output=json&api_key=guest&sdql=date,team,o:team,goals,o:goals,faceoffs won, line, losses, margin, ou margin, ou streak, overtime, penalties, penalty minutes, period scores, playoffs,  shoot out, shots on goal, o:shots on goal, site, total,penalty minutes,o:penalty minutes@(season={})'.format(year)
    headers = {
        'User-Agent': 'curl',
    }
    page = requests.get(url, verify=False, headers=headers)
    raw = page.text.replace('json_callback(', '').replace(');\n', '').replace('\t', '').replace('\'', '"')
    data = json.loads(raw)
    # Uncomment to see field indexes
    # print([[i, data['headers'][i]] for i in range(len(data['headers']))])
    data = data['groups'][0]['columns']
    stats = [{
            'date': data[0][i],
            'team': data[1][i],
            'opp': data[2][i],
            'goals': data[3][i],
            'opp_goals': data[4][i],
            'shots': data[17][i],
            'shots_against': data[18][i],
            'pen_min': data[21][i],
            'pen_min_opp': data[22][i],
        } for i in range(len(data[0]))]
    for game in sorted(stats, key=rank):
        if (game['pen_min'] is not None and game['pen_min_opp'] is not None):
            print('{}, {} vs {}: {} PIMs'.format(nice_date(game['date']), game['team'], game['opp'], game['pen_min'] + game['pen_min_opp']))

def nice_date(date):
    return datetime.strptime(str(date), '%Y%m%d').strftime('%b %d, %Y')

def main(argv):
    usage = 'nhl-rank.py -t <team> -y <year> -w <winner premium>'
    global winner
    team = 'PHI'
    year = '2019'
    try:
      opts, args = getopt.getopt(argv,"ht:w:y:",["team=", "winner=", "year="])
    except getopt.GetoptError:
      print(usage)
      sys.exit(2)
    for opt, arg in opts:
      if opt == '-h':
         print(usage)
         sys.exit()
      elif opt in ("-t", "--team"):
         team = arg
      elif opt in ("-y", "--year"):
         year = arg
      elif opt in ("-w", "--winner"):
         winner = float(arg)
    rank_games(team, year)

if __name__ == "__main__":
   main(sys.argv[1:])
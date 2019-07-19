from bs4 import BeautifulSoup

import re

import teams

with open("example.html") as file:
  soup = BeautifulSoup(file, "html.parser")

  scorebox = soup.find(class_="scorebox")
  performers = scorebox.find_all(itemprop="performer")
  team_info = {}
  for div in performers:
    team = div.find("a", itemprop="name").string
    abbr = teams.team_abbrs_by_name[team]

    # Scores are kept one div up for what are presumably some arcane CSS reasons
    score = div.parent.find("div", class_="score").string
    
    team_info[abbr] = score
  
  winning_team = max(team_info, key=team_info.get)

  penalty_table = soup.find(id="penalty")
  fighting_penalties = penalty_table.find_all(string=re.compile("Fighting|Roughing"))

  print(f"The {teams.team_name_by_abbr[winning_team]} won this game in which " +
    f"there were {len(fighting_penalties)} fighting or roughing penalties.")
file.close()

from bs4 import BeautifulSoup

import re

import teams

###############################################################################
# get_penalties_from_game
#
# Inputs:
#   html: A string of raw html, scraped from a hockey-reference game page
#
# Outputs:
#   A tuple of winner, loser, and number_of_fighting_penalties, where
#   'fighting' encompasses both fighting and roughing penalties.
###############################################################################
def get_penalties_from_game(html):
  soup = BeautifulSoup(html, "html.parser")

  scorebox = soup.find(class_="scorebox")
  performers = scorebox.find_all(itemprop="performer")
  team_info = {}
  for div in performers:
    team = div.find("a", itemprop="name").string
    abbr = teams.team_abbrs_by_name[team]

    # Scores are kept one div up for what are presumably some arcane CSS reasons
    score = div.parent.find("div", class_="score").string
    
    team_info[abbr] = score
  
  winner = max(team_info, key=team_info.get)
  loser = min(team_info, key=team_info.get)

  penalty_table = soup.find(id="penalty")
  fighting_penalties = penalty_table.find_all(string=re.compile("Fighting|Roughing"))

  return (winner, loser, len(fighting_penalties))

###############################################################################
# get_game_urls_from_gamelog
#
# Inputs:
#   html:     A string of raw html, scraped from a hockey-reference team
#             season gamelog
#   base_url: The url of the scraped website because for SOME REASON these
#             hrefs are relative
#
# Outputs:
#   A list of urls of hockey-reference game pages played by that team
###############################################################################
def get_game_urls_from_gamelog(html, base_url):
  soup = BeautifulSoup(html, "html.parser")

  gamelog = soup.find(id="tm_gamelog_rs")
  game_rows = gamelog.find_all(id=re.compile("tm_gamelog_rs."))
  link_containers = [game_row.find(attrs={"data-stat": "date_game"}) for game_row in game_rows]
  links = [base_url + link_container.find("a").get("href") for link_container in link_containers]
  return links
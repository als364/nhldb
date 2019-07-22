from bs4 import BeautifulSoup

import re

import teams

###############################################################################
# get_penalties_from_game
#
# Inputs:
#   html: A string of raw html, scraped from a hockey-reference game page
#   year: The year in which the game took place.
#
# Outputs:
#   A tuple of winner, loser, and number_of_fighting_penalties, where
#   'fighting' encompasses both fighting and roughing penalties.
###############################################################################
def get_penalties_from_game(html, year):
  soup = BeautifulSoup(html, "html.parser")

  scorebox = soup.find(class_="scorebox")
  performers = scorebox.find_all(itemprop="performer")
  team_info = {}
  for div in performers:
    team_link = div.find("a", itemprop="name")['href']
    abbr = re.findall("[A-Z]{3}", team_link)[0]

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
#   html: A string of raw html, scraped from a hockey-reference team
#         season gamelog
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

###############################################################################
# get_series_urls_from_playoffs_summary
#
# Inputs:
#   html: A string of raw html, scraped from a hockey-reference team
#         playoffs summary
#   base_url: The url of the scraped website because for SOME REASON these
#             hrefs are relative
#
# Outputs:
#   A list of urls of hockey-reference series pages
###############################################################################
def get_series_urls_from_playoffs_summary(html, base_url):
  soup = BeautifulSoup(html, "html.parser")

  playoff_table = soup.find(id="all_playoffs")
  link_tags = playoff_table.find_all("a", string=re.compile("View Matchup"))
  links = [base_url + link_container.get("href") for link_container in link_tags]
  return links

###############################################################################
# get_game_urls_from_series
#
# Inputs:
#   html: A string of raw html, scraped from a hockey-reference team
#         playoffs summary
#   base_url: The url of the scraped website because for SOME REASON these
#             hrefs are relative
#
# Outputs:
#   A list of urls of hockey-reference game pages for a playoff series
###############################################################################
def get_game_urls_from_series(html, base_url):
  soup = BeautifulSoup(html, "html.parser")

  content = soup.find(id="content")
  series_table = content.find(class_="game_summaries")
  link_containers = series_table.find_all(class_="gamelink")
  links = [base_url + link_container.find("a").get("href") for link_container in link_containers]
  return links
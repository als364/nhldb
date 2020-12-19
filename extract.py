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
#   A map of period, time, team, player id, penalty, and penalty length.
###############################################################################
def get_penalties_from_game(html):
  soup = BeautifulSoup(html, "html.parser")

  penalties = soup.find(id="all_penalty")
  rows = penalties.find_all("tr")

  penalties = []
  period = ""
  for row in rows:
    if row.find("th"):
      if "OT" in row.find("th").string:
        period = row.find("th").string[0] + "OT"
      else:
        period = row.find("th").string[0]
    else:
      cells = row.find_all("td")
      player_cell = cells[2]
      # removing '/player/_/', where _ is the first letter of their last name,
      # and then the ending '.html'.
      player_id = player_cell.find("a").get("href")[11:-5]
      penalty_text = cells[3].string
      duration = cells[4].string
      # duration = re.sub(f"{duration}..", "", duration)
      duration = duration[:-4]
      
      penalty = {
        "period": period,
        "time": cells[0].string,
        "team": cells[1].string,
        "player_id": player_id,
        "penalty": penalty_text,
        "duration": duration
      }
      penalties.append(penalty)

  return penalties

###############################################################################
# get_fighting_penalties_from_game
#
# Inputs:
#   html: A string of raw html, scraped from a hockey-reference game page
#
# Outputs:
#   A tuple of winner, loser, and number_of_fighting_penalties, where
#   'fighting' encompasses both fighting and roughing penalties.
###############################################################################
def get_fighting_penalties_from_game(html):
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
#   A tuple of list of urls of hockey-reference game pages played by that team
#   - (regular season urls, playoff urls)
###############################################################################
def get_game_urls_from_gamelog(html, base_url):
  soup = BeautifulSoup(html, "html.parser")

  regular_season_gamelog = soup.find(id="tm_gamelog_rs")
  regular_season_game_rows = regular_season_gamelog.find_all(id=re.compile("tm_gamelog_rs."))
  regular_season_link_containers = [game_row.find(attrs={"data-stat": "date_game"}) for game_row in regular_season_game_rows]
  regular_season_links = [base_url + link_container.find("a").get("href") for link_container in regular_season_link_containers]

  playoff_links = []
  playoff_gamelog = soup.find(id="tm_gamelog_po")
  if playoff_gamelog is not None:
    playoff_game_rows = playoff_gamelog.find_all(id=re.compile("tm_gamelog_po."))
    playoff_link_containers = [game_row.find(attrs={"data-stat": "date_game"}) for game_row in playoff_game_rows]
    playoff_links = [base_url + link_container.find("a").get("href") for link_container in playoff_link_containers]
  return (regular_season_links, playoff_links)

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
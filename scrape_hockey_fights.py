from bs4 import BeautifulSoup

import utils
from model.fight import Fight

base_url = "https://hockeyfights.com"

def main():
    get_fights_from_fight_logs(f"{base_url}/fightlog/1/pos2021")


def get_fights_from_fight_logs(fightlog_url):
    fights = []

    print(f"{utils.stringy_now()}: Scraping {fightlog_url}", flush=True)
    fightlog_html = BeautifulSoup(utils.simple_get(fightlog_url), features="html.parser")
    pagination_container = fightlog_html.find("div", {"class": "fightlog-pagination"})
    pages = pagination_container.find_all("a")
    page_urls = [f"{base_url}{page.get('href')}" for page in pages]

    for page_url in page_urls:
        print(f"{utils.stringy_now()}: Scraping{page_url}", flush=True)
        page_html = BeautifulSoup(utils.simple_get(page_url), features="html.parser")
        fight_logs = page_html.find_all("div", {"class": "fight-log"})

        for fight_log in fight_logs:
            players_html = fight_log.find("span", {"class": "players"})
            players_and_teams = [anchor.text for anchor in players_html.find_all("a")]
            date_html = fight_log.find("span", {"class": "date"})
            date_period_time = date_html.find_all("div")
            # First div has date, second has period & time in period
            period_and_time = date_period_time[1].split(" Pd ")

            votes_url = fight_log.find("span", {"class": "link"})
            votes_html = BeautifulSoup(utils.simple_get(f"{base_url}{votes_url})"), features="html.parser")
            results_html = votes_html.find("div", {"class": "voting-results"}).find_all("div", {"class": "option-item"})
            results = {}

            fights.append(Fight(
                players_and_teams[0],
                players_and_teams[2],
                date_period_time[0],
                period_and_time[0],
                period_and_time[1]
            ))


###############################################################################
if __name__ == "__main__":
    main()

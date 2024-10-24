import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)

class ValorantDataCollector:
    def __init__(self):
        self.base_url = "https://www.vlr.gg"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def search_player(self, player_name: str) -> str:
        """Search for a player by name and return their profile URL, filtering for players"""
        search_url = f"{self.base_url}/search/?q={player_name.replace(' ', '%20')}&type=players"
        response = requests.get(search_url, headers=self.headers)
        
        logging.info(f"Request URL: {response.url}")
        logging.info(f"Response status: {response.status_code}")

        if response.status_code != 200:
            logging.error(f"Failed to retrieve search page for {player_name}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        logging.info(f"Page content: {soup.prettify()[:1000]}")

        try:
            player_link = soup.find('a', class_='search-item')

            if player_link:
                profile_url = self.base_url + player_link['href']
                logging.info(f"Found player profile: {profile_url}")
                return profile_url
            else:
                logging.warning(f"Player {player_name} not found in the 'players' category.")
                return None
        except Exception as e:
            logging.error(f"Error parsing search results: {e}")
            return None

    def get_player_stats(self, url: str) -> dict:
        """Extract stats for a single player"""
        url_with_timespan = f"{url}?timespan=all"
        response = requests.get(url_with_timespan, headers=self.headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        name_tag = soup.find('h1', class_='wf-title')
        name = name_tag.text.strip() if name_tag else 'Unknown'

        stats_table = soup.find('table', class_='wf-table')
        stats = []

        if stats_table:
            try:
                stats_rows = stats_table.find('tbody').find_all('tr')
                for row in stats_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        agent_img = cells[0].find('img')
                        agent_name = agent_img['alt'] if agent_img else 'Unknown'

                        usage = cells[1].text.strip()
                        rounds_played = cells[2].text.strip()
                        rating = cells[3].text.strip()
                        acs = cells[4].text.strip()
                        kd = cells[5].text.strip()
                        adr = cells[6].text.strip()
                        kast = cells[7].text.strip()
                        kpr = cells[8].text.strip()
                        apr = cells[9].text.strip()
                        fkpr = cells[10].text.strip()
                        fdpr = cells[11].text.strip()
                        kills = cells[12].text.strip()
                        deaths = cells[13].text.strip()
                        assists = cells[14].text.strip()
                        first_kills = cells[15].text.strip()
                        first_deaths = cells[16].text.strip()

                        stats.append({
                            'Agent': agent_name,
                            'Usage': usage,
                            'Rounds Played': rounds_played,
                            'Rating': rating,
                            'ACS': acs,
                            'K:D': kd,
                            'ADR': adr,
                            'KAST': kast,
                            'KPR': kpr,
                            'APR': apr,
                            'First Kills Per Round': fkpr,
                            'First Deaths Per Round': fdpr,
                            'Kills': kills,
                            'Deaths': deaths,
                            'Assists': assists,
                            'First Kills': first_kills,
                            'First Deaths': first_deaths
                        })

                return {
                    'Name': name,
                    'Stats': stats
                }

            except Exception as e:
                logging.error(f"Error processing player {name}: {str(e)}")
                return None
        else:
            logging.warning(f"Stats table not found for player: {name}")
            return None
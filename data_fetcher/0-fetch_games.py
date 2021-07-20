"""Fetch raw game data from https://map.bemanicn.com

Usage:
  0-fetch_games.py [-o FILE]

Options:
  -h --help             show this message
  -v --version          show version
  -o --output FILE      specify output file [default: ./temp/games.json]
"""
from docopt import docopt
import requests
import json
from bs4 import BeautifulSoup


def fetch_games(output_path):
    games_page = requests.get('https://map.bemanicn.com/games')
    games_soup = BeautifulSoup(games_page.content, 'html.parser')
    games = games_soup.find_all('div', attrs={'class': 'game-container'})
    game_list = []
    for game in games:
        game_id = int(game.parent['href'].split('/')[-1])
        game_title = game.p.text
        game_list.append({
            'id': game_id,
            'title': game_title
        })
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(game_list, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.1')
    output = arguments['--output']
    fetch_games(output)

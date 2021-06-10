"""Fetch data from https://map.bemanicn.com

Usage:
  fetch.py [-s STAGE]

Options:
  -h --help             Show this message.
  -v --version          Show version.
  -s --stage STAGE      STAGE to fetch. Must be in [shop, detail, game].

"""
from docopt import docopt
import requests
import json
from bs4 import BeautifulSoup


def fetch_shops():
    shop_list = {}

    print('Looking for all provinces...')
    region_page = requests.get('https://map.bemanicn.com/region')
    region_soup = BeautifulSoup(region_page.content, 'html.parser')
    province_tiles = region_soup.find_all('div', attrs={'class': 'showUntil-M', 'style': 'margin:0 auto;'})
    provinces = {province_tile.text.strip(): province_tile.a['href'] for province_tile in province_tiles}

    for province, province_url in provinces.items():
        print('Fetching ' + province + '...')
        province_page = requests.get(province_url)
        province_soup = BeautifulSoup(province_page.content, 'html.parser')
        shop_table = province_soup.find('table', attrs={'class': 'nes-table'})
        if shop_table is None:
            print('No shops in ' + province)
            continue
        shop_rows = shop_table.tbody.find_all('tr')
        for shop_row in shop_rows:
            shop_url = shop_row.a['href']
            shop_id = int(shop_url.split('/')[-1])
            column = shop_row.find_all('td')
            shop_name = column[0].text.strip()
            shop_location = column[1].text.strip()
            shop_address = column[2].text.strip()
            shop_list[shop_id] = {
                'id': shop_id,
                'url': shop_url,
                'name': shop_name,
                'province': province,
                'location': shop_location,
                'address': shop_address
            }
    with open('raw/shops.json', 'w', encoding='utf8') as f:
        json.dump(shop_list, f, ensure_ascii=False, indent=2)


def fetch_details(json_path):
    with open(json_path, 'r', encoding='utf8') as i:
        shop_list = json.load(i)
        detail_list = {}
        for shop in shop_list.values():
            print('Fetching ' + shop['name'] + ' (' + str(shop['id']) + ')' + '...')
            shop_page = requests.get(shop['url'])
            shop_soup = BeautifulSoup(shop_page.content, 'html.parser')
            shop_city = shop_soup.find('ul', attrs={'class': 'nes-list is-disc'}).find_all('a')[-1].text.strip()
            shop_commute = shop_soup.find('span', attrs={'id': 'shop-transport'}).text.strip()
            shop_coin_price = shop_soup.find('span', attrs={'id': 'shop-price'}).text.strip()
            shop_desc = shop_soup.find('pre', attrs={'id': 'shop-comment'}).text.strip()
            shop_long = float(shop_soup.find('input', attrs={'id': 'shop-longitude'})['value'])
            shop_lat = float(shop_soup.find('input', attrs={'id': 'shop-latitude'})['value'])

            machine_list = []
            machines = shop_soup.find('table', attrs={'class': 'nes-table'}).tbody.find_all('tr')
            for machine_row in machines:
                machine_row = machine_row.find_all('td')
                machine_list.append({
                    'title': machine_row[0].text.strip(),
                    'title_id': int(machine_row[0].a['href'].split('/')[-1]),
                    'version': machine_row[1].text.strip(),
                    'count': machine_row[2].text.strip(),
                    'coin_per_play': machine_row[3].text.strip(),
                    'desc': machine_row[4].text.strip()
                })

            detail_list[shop['id']] = {
                'id': shop['id'],
                'url': shop['url'],
                'name': shop['name'],
                'province': shop['province'],
                'city': shop_city,
                'district': shop['location'],
                'address': shop['address'],
                'location': {
                    'longitude': shop_long,
                    'latitude': shop_lat
                },
                'commute': shop_commute,
                'coin_price': shop_coin_price,
                'desc': shop_desc,
                'machines': machine_list
            }
        with open('raw/details.json', 'w', encoding='utf8') as f:
            json.dump(detail_list, f, ensure_ascii=False, indent=2)


def fetch_games():
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
    with open('raw/games.json', 'w', encoding='utf8') as f:
        json.dump(game_list, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')
    if arguments['--stage'] == 'game':
        fetch_games()
    else:
        fetch_shops()
        fetch_details('raw/shops.json')

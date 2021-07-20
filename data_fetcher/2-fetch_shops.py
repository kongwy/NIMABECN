"""Fetch raw shop data from https://map.bemanicn.com

Usage:
  2-fetch_shops.py [-o FILE]

Options:
  -h --help             show this message
  -v --version          show version
  -o --output FILE      specify output file [default: ./temp/shops.json]
"""
from docopt import docopt
import requests
import json
from bs4 import BeautifulSoup


def fetch_shops(output_path):
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
    with open(output_path, 'w', encoding='utf8') as f:
        json.dump(shop_list, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.1')
    output = arguments['--output']
    fetch_shops(output)

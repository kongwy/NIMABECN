"""Fetch raw shop detail data from https://map.bemanicn.com

Usage:
  3-fetch_shop_details.py [-i FILE] [-o FILE]

Options:
  -h --help             show this message
  -v --version          show version
  -i --input FILE       specify input file from last stage [default: ./temp/shops.json]
  -o --output FILE      specify output file [default: ./temp/detail.json]
"""
from docopt import docopt
import requests
import json
from bs4 import BeautifulSoup


def fetch_details(input_path, output_path):
    with open(input_path, 'r', encoding='utf8') as i:
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
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(detail_list, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.1')
    source = arguments['--input']
    output = arguments['--output']
    fetch_details(source, output)

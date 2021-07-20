"""Process and generate shop data from fetched

Usage:
  4-process.py [-g FILE] [-r FILE] [-d FILE] [-o FILE]

Options:
  -h --help             show this message
  -v --version          show version
  -g --games FILE       specify _games.json location [default: ./_games.json]
  -r --regions FILE     specify regions.json location [default: ./output/regions.json]
  -d --detail FILE      specify detail.json location [default: ./temp/detail.json]
  -o --output FILE      specify output file [default: ./output/shops.json]
"""
from docopt import docopt
import json


def process_machines(machines, games_path):
    processed = []
    with open(games_path, 'r') as gf:
        games = json.load(gf)
        game_map = {}
        for game in games:
            game_map[game['external']['bcn']] = game['_id']
        for machine in machines:
            game_id = game_map.get(machine['title_id'], None)
            if game_id is None:
                continue
            processed.append({
                'game': game_id,
                'version': machine['version'],
                'count': int(machine['count']),
                'coin_per_play': int(machine['coin_per_play'].split()[0]),
                'description': machine['desc']
            })
        return processed


def process(games_path, regions_path, detail_path, output_path):
    processed = []
    with open(detail_path, 'r', encoding='utf8') as df:
        shops = json.load(df)
        for shop in shops.values():
            # drop shops in HK, MO, TW
            if shop['province'] in ['香港特别行政区', '台湾省', '澳门特别行政区']:
                continue

            # format
            shop_name = shop['name'].replace('(', '（').replace(')', '）')
            shop_price = float(shop['coin_price'].replace('元', ''))
            shop_district = shop['district'].replace(shop['city'], '')

            # change in region level
            if shop['city'] == '市辖区':
                shop['city'] = shop['province']
            elif '直辖县级行政区划' in shop['city']:
                shop['city'] = shop_district
                shop_district = ''

            # convert region to code
            with open(regions_path, 'r') as r:
                regions = json.load(r)
                province_code = get_region_id(shop['province'], regions)['_id']
                city_code = get_region_id(shop['city'], regions)['_id']
                district_code = get_region_id(shop_district, regions, parent=city_code)
                if district_code is not None:
                    district_code = district_code['_id']

            shop_machine = process_machines(shop['machines'], games_path)

            processed.append({
                '_id': shop['id'],
                'name': shop_name,
                'per_coin_price': shop_price,
                'description': shop['desc'],
                'location': {
                    'province': province_code,
                    'city': city_code,
                    'district': district_code,
                    'address': shop['address'],
                    'transport': shop['commute']
                },
                'coordinate': {
                    'type': 'Point',
                    'coordinates': [
                        shop['location']['longitude'],
                        shop['location']['latitude']
                    ]
                },
                'has': shop_machine,
                'external': {
                    'bcn': shop['id'],
                    'amap': '',
                }
            })
        with open(output_path, 'w', encoding='utf8') as wf:
            json.dump(processed, wf, ensure_ascii=False, indent=2)


def get_region_id(name: str, regions: list, parent=None):
    for region in regions:
        if region['name'] == name:
            if parent is None or region['parent'] == parent:
                return region
    return None


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.1')
    game_source = arguments['--games']
    region_source = arguments['--regions']
    detail_source = arguments['--detail']
    output = arguments['--output']
    process(game_source, region_source, detail_source, output)

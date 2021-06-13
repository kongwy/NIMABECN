import json


def process_machines(machines):
    processed = []
    with open('games.json', 'r') as gf:
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


def process(detail_path):
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
            with open('regions.json', 'r') as r:
                regions = json.load(r)
                province_code = get_region_id(shop['province'], regions)['_id']
                city_code = get_region_id(shop['city'], regions)['_id']
                district_code = get_region_id(shop_district, regions, parent=city_code)
                if district_code is not None:
                    district_code = district_code['_id']

            shop_machine = process_machines(shop['machines'])

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
                    'longitude': shop['location']['longitude'],
                    'latitude': shop['location']['latitude']
                },
                'has': shop_machine,
                'external': {
                    'bcn': shop['id'],
                    'amap': '',
                }
            })
        with open('shops.json', 'w', encoding='utf8') as wf:
            json.dump(processed, wf, ensure_ascii=False, indent=2)


def get_region_id(name: str, regions: list, parent=None):
    for region in regions:
        if region['name'] == name:
            if parent is None or region['parent'] == parent:
                return region
    return None


if __name__ == '__main__':
    process('raw/details.json')

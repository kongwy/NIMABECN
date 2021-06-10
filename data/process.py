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
            if shop['province'] in ['香港特别行政区', '台湾省', '澳门特别行政区']:
                continue

            shop_name = shop['name'].replace('(', '（').replace(')', '）')
            shop_price = float(shop['coin_price'].replace('元', ''))
            shop_district = shop['district'].replace(shop['city'], '')
            if shop['city'] == '市辖区':
                shop['city'] = shop['province']

            shop_machine = process_machines(shop['machines'])

            processed.append({
                '_id': shop['id'],
                'name': shop_name,
                'per_coin_price': shop_price,
                'description': shop['desc'],
                'location': {
                    'province': shop['province'],
                    'city': shop['city'],
                    'district': shop_district,
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


if __name__ == '__main__':
    process('raw/details.json')

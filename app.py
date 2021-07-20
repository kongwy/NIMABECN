import time

from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
from pymongo import MongoClient
import yaml

app = Flask(__name__)
api = Api(app)

timer = time.time()

with open('config.yml', 'r') as c:
    config = yaml.load(c, Loader=yaml.Loader)
    db = config['db']
    db_path = 'mongodb://{user}:{passwd}@{host}:{port}/'.format(
        user=db['user'],
        passwd=db['passwd'],
        host=db['host'],
        port=db['port']
    )


def log_time(msg):
    global timer
    print(format(time.time() - timer, '.5f') + ': ' + msg)
    timer = time.time()


def get_games(gid=None):
    log_time('start getting games')
    conn = MongoClient(db_path)['573kw']['games']
    if gid is None:
        r = [d for d in conn.find({})]
    else:
        r = [conn.find_one({'_id': gid})]
    log_time('stop getting games')
    return [process(d) for d in r]


def get_shops(sid=None, limit=None, skip=None):
    log_time('start getting shops')
    conn = MongoClient(db_path)['573kw']['shops']
    if sid is None:
        r = [d for d in conn.find({}).skip(skip).limit(limit)]
        total = conn.count_documents({})
    else:
        r = [conn.find_one({'_id': sid})]
        total = 1
    log_time('stop getting shops')
    return [process(d) for d in r], total


def get_regions(rid=None):
    log_time('start getting regions')
    conn = MongoClient(db_path)['573kw']['regions']
    if rid is None:
        r = [d for d in conn.find({})]
    else:
        r = [conn.find_one({'_id': rid})]
    log_time('stop getting regions')
    return [process(d) for d in r]


def process(d: dict):
    d.update(dict(id=d.pop('_id')))
    return d


def response(data=None,
             paging=False,
             paging_total=None,
             paging_no=None,
             paging_limit=None,
             paging_next=None):
    if (not paging) and (data is None or len(data) == 0):
        abort(404, status=404, message='Resource not found.')
    r = {'status': 200,
         'message': 'OK',
         'data': data
    }
    if paging:
        r.update(dict(paging={
            'total': paging_total,
            'page': paging_no,
            'limit': paging_limit,
            'has_next': paging_next
        }))
    return r


class Game(Resource):
    def get(self, gid=None):
        games = get_games(gid=gid)
        return response(games)


class Shop(Resource):
    def get(self, sid=None):
        global timer
        timer = time.time()
        log_time('receive request')
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, default=20)
        parser.add_argument('page', type=int, default=1)
        args = parser.parse_args()
        page = args.get('page')
        limit = args.get('limit')
        skip = limit * (page - 1)

        shops, total = get_shops(sid=sid, limit=limit, skip=skip)
        paging = (total != 1)
        has_next = (skip + len(shops) < total)

        log_time('start processing query')
        games_d = {g['id']: g for g in get_games()}
        regions_d = {r['id']: r for r in get_regions()}
        shops = [postprocess_shop(s, regions_d, games_d) for s in shops]
        log_time('stop processing query')

        log_time('response request')
        return response(shops,
                        paging=paging,
                        paging_total=total,
                        paging_no=page,
                        paging_limit=limit,
                        paging_next=has_next)


def postprocess_shop(shop, regions_dict, games_dict):
    shop['location']['province'] = regions_dict.get(shop['location']['province'], {}).get('name', None)
    shop['location']['city'] = regions_dict.get(shop['location']['city'], {}).get('name', None)
    shop['location']['district'] = regions_dict.get(shop['location']['district'], {}).get('name', None)

    for machine in shop['has']:
        machine['game_id'] = machine.pop('game')
        machine['title'] = games_dict[machine['game_id']]['title']

    return shop


class Search(Resource):
    def get(self):
        # TODO
        return response()


api.add_resource(Game, '/v1/games', '/v1/games/<int:gid>')
api.add_resource(Shop, '/v1/shops', '/v1/shops/<int:sid>')
api.add_resource(Search, '/v1/search')

if __name__ == '__main__':
    app.config.update(RESTFUL_JSON={
        'indent': 4,
        'ensure_ascii': False
    })
    app.run()

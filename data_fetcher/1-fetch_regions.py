"""Fetch region data from MCA

Usage:
  1-fetch_regions.py [-s SOURCE] [-o FILE]

Options:
  -h --help             show this message
  -v --version          show version
  -s --data-source URL  specify data source [default: http://www.mca.gov.cn/article/sj/xzqh/2020/20201201.html]
  -o --output FILE      specify output file [default: ./output/regions.json]
"""
from docopt import docopt
import requests
import json
from bs4 import BeautifulSoup


def fetch_regions(source_url, output_path):
    print('Fetching all provinces...')
    r = requests.get(source_url)
    bs = BeautifulSoup(r.content, 'html.parser')
    region_rows = bs.find_all('tr', attrs={'height': '19'})
    regions = []
    for row in region_rows:
        cells = row.find_all('td')
        region_id = cells[1].text.strip()
        if region_id == '':
            continue
        region_id = int(region_id)
        region_name = cells[2].text.strip()
        region = {
            '_id': region_id,
            'name': region_name
        }
        t, m, b = int(region_id / 10000), int(region_id / 100) % 100, region_id % 100
        if b != 0 and t not in [11, 12, 31, 50] and m not in [90]:
            region['parent'] = t * 10000 + m * 100
        elif m != 0:
            region['parent'] = t * 10000
        else:
            region['parent'] = None
        print(region_name + ' fetched. ')
        regions.append(region)
    with open(output_path, 'w', encoding='utf8') as w:
        json.dump(regions, w, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.1')
    source = arguments['--data-source']
    output = arguments['--output']
    fetch_regions(source, output)

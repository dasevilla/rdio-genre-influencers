# coding=utf-8

from collections import defaultdict
from time import sleep
import json
import logging
import string

from pyechonest import config as echo_nest_config, artist as echo_nest_artist
from requests.auth import AuthBase
import requests


RDIO_API_URL = 'https://www.rdio.com/api/1/'
RDIO_API_TOKEN = ''
ECHO_NEST_API_KEY = ''

ECHO_NEST_GENRE = 'comedy'
ECHO_NEST_GENRE_SORT = 'hotttnesss-desc'
ECHO_NEST_GENRE_SIZE = 30

DEFAULT_RDIO_LISTNER_COUNT = 100
RDIO_API_RATE_LIMIT = 1  # in seconds

ECHO_NEST_SORT_TYPES = [
    'familiarity-asc',
    'familiarity-desc',
    'hotttnesss-asc',
    'hotttnesss-desc',
    'artist_start_year-asc',
    'artist_start_year-desc',
    'artist_end_year-asc',
    'artist_end_year-desc',
]


ECHO_NEST_GENRE_FILE_SAFE = string.replace(ECHO_NEST_GENRE, ' ', '-')
GENERE_ARTIST_FILE = '%s_artists.json' % ECHO_NEST_GENRE_FILE_SAFE
GENERE_LISTENER_FILE = '%s_listners.json' % ECHO_NEST_GENRE_FILE_SAFE
GENERE_INFLUENCER_FILE = '%s_influencers.json' % ECHO_NEST_GENRE_FILE_SAFE

echo_nest_config.ECHO_NEST_API_KEY = ECHO_NEST_API_KEY


class BearerAuth(AuthBase):
    """Adds a HTTP Bearer token to the given Request object."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = 'Bearer %s' % self.token
        return r


def get_recent_listners(rdio_key, start=0, count=10):
    """
    Returns a list of Rdio User objects
    """

    payload = {
        'method': 'getRecentListeners',
        'key': rdio_key,
        'extras': 'User.shortUrl',
        'start': start,
        'count': count,
    }
    r = requests.post(RDIO_API_URL, auth=BearerAuth(RDIO_API_TOKEN), data=payload)
    return r.json()['result']


def main_influencers():
    listner_data = None
    with open(GENERE_LISTENER_FILE, 'r') as fd:
        listner_data = json.load(fd)

    if listner_data is None:
        return

    all_listners = {}
    listner_count = defaultdict(list)
    for rdio_artist_key, rdio_listners in listner_data.iteritems():
        for rdio_user in rdio_listners:
            rdio_user_key = rdio_user['key']

            if rdio_user_key not in all_listners:
                all_listners[rdio_user_key] = rdio_user

            listner_count[rdio_user_key].append(rdio_artist_key)

    listner_count_sorted = sorted(listner_count.iteritems(),
                                  key=lambda item: len(item[1]), reverse=True)

    full_list = []
    for rdio_user_key, _ in listner_count_sorted:
        full_list.append(all_listners[rdio_user_key])

    with open(GENERE_INFLUENCER_FILE, 'w') as fp:
        json.dump(full_list, fp, indent=2)


def main_listners():
    genre_artists = None

    with open(GENERE_ARTIST_FILE, 'r') as fp:
        genre_artists = json.load(fp)

    listners_dict = defaultdict(list)
    for genre_artist in genre_artists:
        rdio_artist_key = genre_artist['key']
        users = get_recent_listners(rdio_artist_key,
                                    count=DEFAULT_RDIO_LISTNER_COUNT)

        for user in users:
            listners_dict[rdio_artist_key].append({
                'key': user['key'],
                'name': '%s %s' % (user['firstName'], user['lastName']),
                'shortUrl': user['shortUrl'],
            })
        sleep(RDIO_API_RATE_LIMIT)

    with open(GENERE_LISTENER_FILE, 'w') as fp:
        json.dump(listners_dict, fp, indent=2)


def main_search():
    """
    http://developer.echonest.com/docs/v4/artist.html#search
    http://echonest.github.io/pyechonest/artist.html#pyechonest.artist.search
    """

    results = echo_nest_artist.search(
        style=ECHO_NEST_GENRE,
        limit=True,
        buckets=['id:rdio-US'],
        sort=ECHO_NEST_GENRE_SORT,
        start=0,
        results=ECHO_NEST_GENRE_SIZE,
    )

    artist_keys = [extract_rdio_key(artist) for artist in results]

    payload = {
        'method': 'get',
        'keys': ','.join(artist_keys),
    }
    r = requests.post(RDIO_API_URL, auth=BearerAuth(RDIO_API_TOKEN), data=payload)

    result_json = r.json()['result']

    artist_list = []
    for rdio_key in artist_keys:
        if rdio_key not in result_json:
            logging.warn('Rdio response was missing %s', rdio_key)
            continue

        artist_json = result_json[rdio_key]

        artist_list.append({
            'key': artist_json['key'],
            'name': artist_json['name'],
            'shortUrl': artist_json['shortUrl'],
        })

    with open(GENERE_ARTIST_FILE, 'w') as fd:
        json.dump(artist_list, fd, indent=2)


def extract_rdio_key(artist):
    rdio_region = 'US'
    raw_key = artist.get_foreign_id('rdio-%s' % rdio_region)
    return raw_key.split(':')[2]


if __name__ == '__main__':
    main_search()
    main_listners()
    main_influencers()

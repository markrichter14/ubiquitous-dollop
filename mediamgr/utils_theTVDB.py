'''
    theTvDb API
'''
import time
#import json
import requests

TIMEOUT = 10

def get_id_tuple(f, args, kwargs, mark=object()):
    """
    Some quick'n'dirty way to generate a unique key for an specific call.
    """
    # l = [id(f)]
    # for arg in args:
    #     l.append(id(arg))
    # #l.append(id(mark))
    # for k, v in kwargs:
    #     l.append(k)
    #     l.append(id(v))
    l = []
    for arg in args:
        l.append(arg)
    for k, v in kwargs:
        l.append(k)
        l.append(v)
    return tuple(l)

def memoize_with_limit(func):
    """
        memoize with time limit
    """
    cache = {}
    LIMIT = 60*60 # seconds in 1 hour
    def memoized(*args, **kwargs):
        print('memoized')
        now = int(time.time())
        print(now)
        key = get_id_tuple(func, args, kwargs)
        print('key:', key)
        missing = key not in cache
        print('missing:', missing)
        if missing or (now - cache[key]['retrieved'] > LIMIT):
            res = func(*args, **kwargs)
            if res:
                print('add/update')
                cache[key] = {'result': res, 'retrieved': now}
            elif missing:
                print('missing/null')
                cache[key] = {'result': None, 'retrieved': 0}
        print('size:', len(cache))
        return cache[key]['result']
    return memoized

class TheTVDB_API():
    '''
        encapsilate TheTVDB API requests
    '''

    BASE_URL = 'https://api.thetvdb.com'
    TIMEOUT = 10

    def __init__(self, username, unique_id, api_key):
        print('\nCall: init')
        self.api_key = api_key
        self.unique_id = unique_id
        self.username = username
        self.token = self.get_token()

    def get_token(self):
        '''
            Error 401
        '''
        print('\nCall: get_token')
        url = self.BASE_URL + '/login'
        payload = {'apikey': self.api_key,
                   'userkey': self.unique_id,
                   'username': self.username}
        req = requests.post(url, json=payload)
        req.raise_for_status()
        req = req.json()
        return req['token']

    def refresh_token(self):
        '''
            Error 401
        '''
        print('\nCall: refresh_token')
        url = self.BASE_URL + '/refresh_token'
        headers = {'Authorization' : 'Bearer ' + self.token}
        req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 401:
            return self.get_token()
        req.raise_for_status()
        req = req.json()
        return req['token']

    @memoize_with_limit
    def search_series_params(self):
        '''
            Error 401
        '''
        print('\nCall: get_series_params')
        url = self.BASE_URL + '/search/series/params'
        headers = {'Authorization' : 'Bearer ' + self.token}
        req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 401:
            self.token = self.refresh_token()
            headers = {'Authorization' : 'Bearer ' + self.token}
            req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 200:
            req = req.json()
            return req['data']['params']
        return None

    @memoize_with_limit
    def search_series(self, name=None, imdb_id=None):
        '''
            Error 401, 404
        '''
        print('\nCall: search_series - {}'.format(str(name) if name else str(imdb_id)))
        if not name and not imdb_id:
            return None
        url = self.BASE_URL + '/search/series'
        headers = {'Authorization' : 'Bearer ' + self.token}
        if name:
            payload = {'name': name}
        else:
            payload = {'imdbId': imdb_id}
        req = requests.get(url, headers=headers, params=payload,
                           timeout=self.TIMEOUT)
        if req.status_code == 401:
            self.token = self.refresh_token()
            headers = {'Authorization' : 'Bearer ' + self.token}
            req = requests.get(url, headers=headers, params=payload,
                               timeout=self.TIMEOUT)
        if req.status_code == 200:
            req = req.json()
            return req.get('data')
        return None

    @memoize_with_limit
    def series(self, series_id):
        '''
            Error 401, 404
        '''
        print('\nCall: series - {}'.format(series_id))
        url = self.BASE_URL + '/series/{}'.format(series_id)
        headers = {'Authorization' : 'Bearer ' + self.token}
        req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 401:
            self.token = self.refresh_token()
            headers = {'Authorization' : 'Bearer ' + self.token}
            req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 200:
            req = req.json()
            return req.get('data')
        return None



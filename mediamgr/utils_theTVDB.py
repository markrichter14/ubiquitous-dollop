'''
    theTVDB API
'''
import requests, json
import time

TIMEOUT = 10

class TheTVDB_API(object):

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
        r = requests.post(url, json=payload)
        r.raise_for_status()
        d = r.json()
        return d['token']
        
    def refresh_token(self):
        '''
            Error 401
        '''
        print('\nCall: refresh_token')
        url = self.BASE_URL + '/refresh_token'
        headers = {'Authorization' : 'Bearer ' + self.token}
        r = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if r.status_code == 401:
            return self.get_token()
        r.raise_for_status()
        d = r.json()
        return d['token']
        
    def get_series_params(self):
        '''
            Error 401
        '''
        print('\nCall: get_series_params')
        url = self.BASE_URL + '/search/series/params'
        headers = {'Authorization' : 'Bearer ' + self.token}
        r = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if r.status_code == 401:
            self.token = self.refresh_token()
            headers = {'Authorization' : 'Bearer ' + self.token}
            r = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        d = r.json()
        return d['data']['params']
        
    search_series_memo = {}
    
    def search_series(self, name=None, imdb_id=None):
        '''
            Error 401, 404
        '''
        print('\nCall: search_series - {}'.format(str(name) if name else str(imdb_id)))
        if not name and not imdb_id:
            #return None
            raise ValueError('No parameter given')
        
        now = int(time.time())
        limit = 60*60 # seconds in 1 hour
        if ((name, imdb_id) not in self.search_series_memo or 
            (now - self.search_series_memo[(name, imdb_id)]['retrieved'] > limit)):
            url = self.BASE_URL + '/search/series'
            headers = {'Authorization' : 'Bearer ' + self.token}
            if name:
                payload = {'name': name}
            else:
                payload = {'imdbId': imdb_id}
            r = requests.get(url, headers=headers, params=payload, 
                                timeout=self.TIMEOUT)
            if r.status_code == 401:
                self.token = self.refresh_token()
                headers = {'Authorization' : 'Bearer ' + self.token}
                r = requests.get(url, headers=headers, params=payload, 
                                    timeout=self.TIMEOUT)
            d = r.json()
            result = d.get('data')
            if result:
                self.search_series_memo[(name, imdb_id)] = {'data': result, 
                                                            'retrieved': now}
            elif (name, imdb_id) not in self.search_series_memo:
                return None
        return self.search_series_memo[(name, imdb_id)]['data']


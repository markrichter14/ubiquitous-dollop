'''
    theTvDb API
'''
import requests
from mediamgr.utils import memoize_with_limit

TIMEOUT = 10

class TheTVDB_API():
    '''
        encapsilate TheTVDB API requests
    '''

    BASE_URL = 'https://api.thetvdb.com'
    TIMEOUT = 10

    def __init__(self, username, unique_id, api_key):
        # print('\nCall: init')
        self.api_key = api_key
        self.unique_id = unique_id
        self.username = username
        self.token = self.get_token()

    def get_token(self):
        '''
            Error 401
        '''
        # print('\nCall: get_token')
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
        # print('\nCall: refresh_token')
        url = self.BASE_URL + '/refresh_token'
        headers = {'Authorization' : 'Bearer ' + self.token}
        req = requests.get(url, headers=headers, timeout=self.TIMEOUT)
        if req.status_code == 401:
            return self.get_token()
        req.raise_for_status()
        req = req.json()
        return req['token']

    @memoize_with_limit
    def search_series(self, name=None, imdb_id=None):
        '''
            Error 401, 404
        '''
        # print('\nCall: search_series - {}'.format(str(name) if name else str(imdb_id)))
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
    def search_series_params(self):
        '''
            Error 401
        '''
        # print('\nCall: get_series_params')
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
    def series(self, series_id):
        '''
            Error 401, 404
        '''
        # print('\nCall: series - {}'.format(series_id))
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

    @memoize_with_limit
    def series_episodes_query(self, series_id, season=None, episode=None, page=1):
        '''
            This route allows the user to query against episodes for the given
            series. The response is a paginated array of episode records.

            {"data": [{ "absoluteNumber": 0,
                        "airedEpisodeNumber": 0,
                        "airedSeason": 0,
                        "airsAfterSeason": 0,
                        "airsBeforeEpisode": 0,
                        "airsBeforeSeason": 0,
                        "director": "string",
                        "directors": ["string"],
                        "dvdChapter": 0,
                        "dvdDiscid": "string",
                        "dvdEpisodeNumber": 0,
                        "dvdSeason": 0,
                        "episodeName": "string",
                        "filename": "string",
                        "firstAired": "string",
                        "guestStars": ["string"],
                        "id": 0,
                        "imdbId": "string",
                        "lastUpdated": 0,
                        "lastUpdatedBy": "string",
                        "overview": "string",
                        "productionCode": "string",
                        "seriesId": "string",
                        "showUrl": "string",
                        "siteRating": 0,
                        "siteRatingCount": 0,
                        "thumbAdded": "string",
                        "thumbAuthor": 0,
                        "thumbHeight": "string",
                        "thumbWidth": "string",
                        "writers": ["string"]}],
            "errors": { "invalidFilters": ["string"],
                        "invalidLanguage": "string",
                        "invalidQueryParams": ["string"]},
            "links": {  "first": 0,
                        "last": 0,
                        "next": 0,
                        "previous": 0} }

            May return Errors 401, 404, 405
        '''
        # print('\nCall: series_episodes_query - {} {} {} {}'.format(series_id,
        #                                                            season,
        #                                                            episode,
        #                                                            page))
        url = self.BASE_URL + '/series/{}/episodes/query'.format(series_id)
        headers = {'Authorization' : 'Bearer ' + self.token}
        payload = {'page': page}
        if season is not None:
            payload['airedSeason'] = season
        if episode is not None:
            payload['airedEpisode'] = episode
        # print('payload:', payload)
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
    def series_episodes_summary(self, series_id):
        '''
            Error 401, 404
        '''
        # print('\nCall: series_episodes_summary - {}'.format(series_id))
        url = self.BASE_URL + '/series/{}/episodes/summary'.format(series_id)
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

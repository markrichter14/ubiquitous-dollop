import requests, json

BASE_URL = 'https://api.thetvdb.com'

def get_token(username, unique_id, api_key):
    '''
        Error 401
    '''
    url_ext = '/login'
    url = BASE_URL + url_ext
    payload = {'apikey': api_key, 'userkey': unique_id, 'username': username}
    r = requests.post(url, json=payload)
    d = r.json()
    return d['token']
    
def refresh_token(token):
    '''
        Error 401
    '''
    url_ext = '/refresh_token'
    url = BASE_URL + url_ext
    headers = {'Authorization' : 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    d = r.json()
    return d['token']
    
def get_series_params(token):
    '''
        Error 401
    '''
    url_ext = '/search/series/params'
    url = BASE_URL + url_ext
    headers = {'Authorization' : 'Bearer ' + token}
    r = requests.get(url, headers=headers)
    d = r.json()
    return d['data']['params']
    
def search_series(token, name=None, imdb_id=None):
    '''
        Error 401, 404
    '''
    if not name and not imdb_id:
        #return None
        raise ValueError('No parameter given')
    url_ext = '/search/series'
    url = BASE_URL + url_ext
    headers = {'Authorization' : 'Bearer ' + token}
    if name:
        payload = {'name': name}
    else:
        payload = {'imdbId': imdb_id}
    r = requests.get(url, headers=headers, params=payload)
    print(r)
    d = r.json()
    return d.get('data')
    


#token = get_token(username, unique_id, api_key)

token = refresh_token(token)

# r = search_series(token, 'dark')
# print(r)

r = search_series(token, 'Family guy')
print(r)




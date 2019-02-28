#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mediamgr.utils.py

Created on Sun Feb 17 12:35:26 2019

@author: Mark Richter

from mediamgr.utils import (VALID, rm_extra_files, tmdb, parse_movie_fn, 
                            get_data, fix_filename)
"""

import os
import urllib.request
import re
import json
from pathlib import Path
import shutil
import time

VALID = [".mp4", ".avi", ".srt", ".m4v", ".mkv", ".mpg"]

def rm_extra_files(dir_path):
    ''' 
        takes a path and deletes all files with VALID file extension,
        and deletes empty directories
        return largest remaining file
    '''
    big_name = None
    big_size = 0
    items = os.scandir(dir_path)
    for item in items:
        if item.is_file():
            pos = item.name.rfind('.')
            dot_ext = item.name[pos:]
            if dot_ext.lower() not in VALID or item.name == 'sample.avi':
                # TODO add logging
                os.remove(item.path)
            else:
                current_size = os.path.getsize(item.path)
                if current_size > big_size:
                    big_name = item.path
                    big_size = current_size
        else: 
            big_dir = rm_extra_files(item.path)
            if not os.listdir(item.path):
                # TODO add logging
                os.rmdir(item.path)
            else:
                if big_dir[1] > big_size:
                    big_name = big_dir[0]
                    big_size = big_dir[1]
    return (big_name, big_size)

class CacheLimited:

    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args):
        now = int(time.time())
        limit = 60*60 # seconds in 1 hour
        if ((args not in self.memo) or 
             (now - self.memo[args]['retrieved'] > limit)):
            result = self.f(*args)
            if (result['http_status'] == 200):
                self.memo[args] = {'data': result, 'retrieved': now}
            elif args not in self.memo:
                return result
        return self.memo[args]['data']
    
@CacheLimited
def tmdb(title, year=None):
    ''' 
        themoviedb.org http request
        returns {'http_status': _, 'http_reason': _, 'total_results': _, 
                 'results':[{'title': _, 'original_title': _, 'release_date': _, 
                             'overview': _, 'poster_path': _}, ...]}
    '''
    tmdb_img_path = 'https://image.tmdb.org/t/p/original'
    api_key = 'ab8926900028eeccb37886fa6702ad75'
    url_base_str = ('https://api.themoviedb.org/3/search/movie?api_key={}' + 
                     '&language=en-US&query={}&page=1')
    url_str = url_base_str.format(api_key, title.replace(' ', '%20'))
    if year:
        url_str += '&year={}'.format(year)
    # TODO add error handling
    http = urllib.request.urlopen(url_str)
    resp_bytes = http.read()
    resp_str = resp_bytes.decode('UTF-8')
    data = json.loads(resp_str)
    
    res = {}
    res['http_status'] = http.status
    res['http_reason'] = http.reason
    if http.status == 200:
        res['total_results'] = data['total_results']
        res['results'] = []
        for i in range(data['total_results']):
            result = {}
            result['title'] = data['results'][i]['title']
            result['order'] = i
            result['id'] = data['results'][i]['id']
            result['original_title'] = data['results'][i]['original_title']
            result['release_date'] = data['results'][i]['release_date']
            result['overview'] = data['results'][i]['overview']
            if data['results'][i]['poster_path']:
                result['poster_path'] = (tmdb_img_path + 
                                          data['results'][i]['poster_path'])
            res['results'].append(result)
    return res

def parse_movie_fn(fn):
    ''' 
        takes movie filename
        returns ('title', 'year')
        assumes year exists in filename
    '''
    p_str = r"(.*)[\W\s]+(19\d{2}|20\d{2})(?!.*^19\d{2}|20\d{2}.*)"
    p = re.compile(p_str)
    m = p.match(fn)
    
    title = m.group(1).rstrip(' ._').replace('.', ' ')
    year = m.group(2)
    return (title, year)

def get_data(file_path):
    ''' 
        Encapsulates parsing and web request
        returns selected info as dict
    '''
    p = Path(file_path)
    search = parse_movie_fn(p.name)
    proposed = '{} ({})'.format(*search)
    download = tmdb(*search)
    if download['http_status'] == 200 and download['total_results'] > 0:
        r = download['results'][0]
        proposed = '{} ({})'.format(r['title'], r['release_date'][:4])
    proposed = fix_filename(proposed)
    return {'filename' : p.name, 
            'path'     : str(p.parent),
            'download' : download,
            'search'   : search,
            'proposed' : proposed}

def fix_filename(fn):
    '''
        strips whitespace and convert illegal linux filename chars to '_'
    '''
    bad_chars = r'\/:*"|?'
    return ''.join([c if c not in bad_chars else '_' for c in fn.strip()])
   
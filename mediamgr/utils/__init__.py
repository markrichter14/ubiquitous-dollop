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
# VIDEO = [".mp4", ".avi", ".m4v", ".mkv", ".mpg"]

def rm_extra_files(dir_path):
    '''
        takes a path and deletes all files with VALID file extension,
            and deletes empty directories
        returns largest remaining file, and size
    '''
    big_name = None
    big_size = float('-inf')
    items = os.scandir(dir_path)
    for item in items:
        if item.is_file():
            pos = item.name.rfind('.')
            dot_ext = item.name[pos:]
            if dot_ext.lower() not in VALID or item.name.lower() == 'sample.avi':
                # TODO add logging
                print('deleting (not valid file):', item)
                os.remove(item.path)
            else:
                current_size = os.path.getsize(item.path)
                if current_size > big_size:
                    big_name = item.path
                    big_size = current_size
        else:
            if item.name.lower() in ['sample']:
                # TODO add logging
                print('deleting ("sample" dir):', item)
                shutil.rmtree(item.path)
            else:
                big_dir = rm_extra_files(item.path)
                if not os.listdir(item.path):
                    # TODO add logging
                    print('deleting (empty dir):', item)
                    os.rmdir(item.path)
                else:
                    if big_dir[1] > big_size:
                        big_name = big_dir[0]
                        big_size = big_dir[1]
    return (big_name, big_size)

def get_id_tuple(func, args, kwargs):
    """
    Some quick'n'dirty way to generate a unique key for a specific call.
    """
    # print('func', func)
    # print('args', args)
    # print('kwargs', kwargs)
    lst = [func]
    for arg in args:
        lst.append(arg)
    for key, val in kwargs.items():
        lst.append((key, val))
    return tuple(lst)

def memoize_with_limit(func):
    """
        memoize with time limit
    """
    cache = {}
    limit = 60*60 # seconds in 1 hour
    def memoized(*args, **kwargs):
        # print('memoized')
        now = int(time.time())
        # print(now)
        key = get_id_tuple(func, args, kwargs)
        # print('key:', key)
        missing = key not in cache
        # print('missing:', missing)
        if missing or (now - cache[key]['retrieved'] > limit):
            res = func(*args, **kwargs)
            if res:
                # print('add/update')
                cache[key] = {'result': res, 'retrieved': now}
            elif missing:
                # print('missing/null')
                cache[key] = {'result': None, 'retrieved': 0}
        # print('size:', len(cache))
        return cache[key]['result']
    return memoized

@memoize_with_limit
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

def parse_movie_fn(filename):
    '''
        takes movie filename
        returns ('title', 'year')
        assumes year exists in filename
    '''
    pattern_str = r"(.*)[\W\s]+(19\d{2}|20\d{2})(?!.*^19\d{2}|20\d{2}.*)"
    pattern = re.compile(pattern_str)
    match = pattern.match(filename)
    if match:
        title = match.group(1).rstrip(' ._').replace('.', ' ')
        year = match.group(2)
        return (title, year)
    return None

def get_data(file_path):
    '''
        Encapsulates parsing and web request
        returns selected info as dict
    '''
    print('file_path', file_path)
    pth = Path(file_path)
    search = parse_movie_fn(pth.name)
    if not search:
        return {'filename' : pth.name,
                'path'     : str(pth.parent),
                'download' : None,
                'search'   : search,
                'proposed' : ''}
    proposed = '{} ({})'.format(*search)
    download = tmdb(*search)
    if download['http_status'] == 200 and download['total_results'] > 0:
        res = download['results'][0]
        proposed = '{} ({})'.format(res['title'], res['release_date'][:4])
    proposed = fix_filename(proposed)
    return {'filename' : pth.name,
            'path'     : str(pth.parent),
            'download' : download,
            'search'   : search,
            'proposed' : proposed}

def fix_filename(filename):
    '''
        strips whitespace and convert illegal linux filename chars to '_'
    '''
    bad_chars = r'\/:*"|?'
    return ''.join([c if c not in bad_chars else '_' for c in filename.strip()])

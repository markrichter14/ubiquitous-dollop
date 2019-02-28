import os, requests
from flask import render_template, redirect, flash, url_for
from mediamgr import app
from mediamgr.utils import (VALID, rm_extra_files, tmdb, parse_movie_fn, 
                            get_data, fix_filename)
from mediamgr.forms import MovieForm, LoginForm

movie_dir = app.config['MOVIE_DIR']
TV_DIR = app.config['TV_DIR']
MOVIE_DEST = app.config['MOVIE_DEST']

@app.route('/')
@app.route('/home')
def home():
    nums = {'movies': 0, 'episodes': 0}
    movie_items = (os.scandir(movie_dir))
    nums['movies'] = sum(1 for _ in movie_items)
    tv_items = (os.scandir(TV_DIR))
    nums['episodes'] = sum(1 for _ in tv_items)
    return render_template('home.html', title='Home', nums=nums)

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    # create folders for files with valid extension, rm junk
    entries = []
    movie_items = (os.scandir(movie_dir))
    for item in movie_items:
        if item.is_file():
            pos = item.name.rfind('.')
            dot_ext = item.name[pos:]
            if dot_ext not in VALID:
                os.remove(item.path)
                # TODO logging
            else: 
                dir_name = item.name[:pos]
                path = movie_dir + dir_name + '/'
                os.mkdir(path)
                file_path = path + item.name
                os.rename(item.path, file_path)
                # TODO logging
                entries.append(get_data(file_path))
        else:
            file_path, __ = rm_extra_files(item.path)
            entries.append(get_data(file_path))

    form = MovieForm()
    if form.validate_on_submit():
        new_dir_name = fix_filename(form.dir_name.data)
        flash('Moved {} to {}'.format(form.file_name.data, new_dir_name))
        os.rename(form.path_name.data, MOVIE_DEST+new_dir_name)
        # TODO move to OSMC
        return redirect(url_for('movies'))
    return render_template('movies.html', title='Movies',
                           entries=entries, form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@app.route('/episodes')
def episodes():
    return render_template('episodes.html', title='Episodes')

def search_series(token, name=None, imdb_id=None):
    '''
        Error 401, 404
    '''
    if not name and not imdb_id:
        #return None
        raise ValueError('No parameter given')
    url = app.config['THETVDB']['BASE_URL'] + '/search/series'
    headers = {'Authorization' : 'Bearer ' + token}
    if name:
        payload = {'name': name}
    else:
        payload = {'imdbId': imdb_id}
    r = requests.get(url, headers=headers, params=payload)
    d = r.json()
    return d.get('data')
    
@app.route('/shows')
def shows():
    entries = []
    shows = []
    fn = 'show_list.txt'
    token = app.config['THETVDB']['TOKEN']
    with open(fn) as f:
        shows.extend(f.readlines())
    for show in shows:
        s = {}
        s['dir_name'] = show.strip()
        d = search_series(token, show)
        s['data'] = d
        entries.append(s)

    return render_template('shows.html', title='Shows', entries=entries)



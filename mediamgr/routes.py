'''
    routes.py
'''
import os
from flask import render_template, redirect, flash, url_for
from werkzeug.utils import secure_filename
from mediamgr import app, db
from mediamgr.utils import (VALID, rm_extra_files, tmdb, parse_movie_fn,
                            get_data, fix_filename)
from mediamgr.forms import (MovieForm, LoginForm, ShowForm, NewShowsForm)
from mediamgr.models import Show, Season, Episode, NewShow
from mediamgr.utils_theTVDB import TheTVDB_API

MOVIE_DIR = app.config['MOVIE_DIR']
TV_DIR = app.config['TV_DIR']
MOVIE_DEST = app.config['MOVIE_DEST']

API = TheTVDB_API(app.config['THETVDB']['USERNAME'],
                  app.config['THETVDB']['UNIQUE_ID'],
                  app.config['THETVDB']['API_KEY'])

@app.route('/')
@app.route('/home')
def home():
    '''
        home page
    '''
    nums = {'movies': 0, 'episodes': 0}
    movie_items = (os.scandir(MOVIE_DIR))
    nums['movies'] = sum(1 for _ in movie_items)
    tv_items = (os.scandir(TV_DIR))
    nums['episodes'] = sum(1 for _ in tv_items)
    return render_template('home.html', title='Home', nums=nums)

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    '''
        movie page: finds downloads in MOVIE_DIR, parses title and year,
        displays info from TMDB, proposes dir name, and moves to media drive
    '''
    # create folders for files with valid extension, rm junk
    entries = []
    movie_items = (os.scandir(MOVIE_DIR))
    for item in movie_items:
        if item.is_file():
            pos = item.name.rfind('.')
            dot_ext = item.name[pos:]
            if dot_ext not in VALID:
                os.remove(item.path)
                # TODO logging
            else:
                dir_name = item.name[:pos]
                path = MOVIE_DIR + dir_name + '/'
                os.mkdir(path)
                file_path = path + item.name
                os.rename(item.path, file_path)
                # TODO logging
                entries.append(get_data(file_path))
        else: # item.is_dir()
            file_path, __ = rm_extra_files(item.path)
            entries.append(get_data(file_path))

    form = MovieForm()
    if form.validate_on_submit():
        new_dir_name = fix_filename(form.dir_name.data)
        flash('Moved {} to {}'.format(form.file_name.data, new_dir_name))
        os.rename(form.path_name.data, MOVIE_DEST+new_dir_name)
        # TODO move to OSMC via SMB
        return redirect(url_for('movies'))
    return render_template('movies.html', title='Movies',
                           entries=entries, form=form)

@app.route('/login')
def login():
    '''
        sample login page
    '''
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@app.route('/new_shows', methods=['GET', 'POST'])
def new_shows():
    '''
        page to add new show to db
    '''
    print('new_shows')
    form = NewShowsForm()
    if form.validate_on_submit():
        new_shows_to_add = []
        if form.new_show_names.data:
            new_shows_to_add.extend(form.new_show_names.data.splitlines())
        if form.text_file.data:
            file_stor = form.text_file.data
            filename = secure_filename(file_stor.filename)
            full_path = os.path.join(app.instance_path, 'temp', filename)
            file_stor.save(full_path)
            with open(full_path) as temp_file:
                new_shows_to_add.extend(temp_file.readlines())
            os.remove(full_path)
        if new_shows_to_add:
            for line in new_shows_to_add:
                name = line.strip()
                ns_db = NewShow.query.filter_by(new_show_name=name).first()
                if not ns_db:
                    new_show_to_add = NewShow(new_show_name=name)
                    db.session.add(new_show_to_add)
            db.session.commit()
        return redirect(url_for('add_shows'))
    return render_template('new_shows.html', title='New Shows', form=form)

@app.route('/delete_new_show/<int:ns_id>', methods=['POST'])
def delete_new_show(ns_id):
    '''
        removes a single new show from db
    '''
    new_show_to_del = NewShow.query.get_or_404(ns_id)
    db.session.delete(new_show_to_del)
    db.session.commit()
    flash('NewShow {} deleted!'.format(new_show_to_del.new_show_name))
    return redirect(url_for('add_shows'))

@app.route('/clr_new_show', methods=['POST'])
def clr_new_show():
    '''
        removes all stored new shows entries from db
    '''
    new_shows_qry = NewShow.query.all()
    for show in new_shows_qry:
        db.session.delete(show)
        flash('NewShow {} deleted!'.format(show.new_show_name))
    db.session.commit()
    return redirect(url_for('new_shows'))

@app.route('/add_shows', methods=['GET', 'POST'])
def add_shows():
    '''
        page to add shows from new shows stored in db
    '''
    entries = []
    new_shows_qry = NewShow.query.all()
    for show in sorted(new_shows_qry, key=lambda ns: ns.new_show_name):
        entry = {}
        entry['name'] = show.new_show_name
        entry['id'] = show.new_show_id
        data = API.search_series(show.new_show_name)
        matches = False
        if data:
            for data_item in data:
                data_item['fixed'] = fix_filename(data_item['seriesName'])
                if Show.query.filter_by(theTVDB_id=data_item['id']).all():
                    data_item['exists'] = True
                    matches |= True
            entry['data'] = data[:3]
        entry['matches'] = matches
        entries.append(entry)

    form = ShowForm()
    if form.validate_on_submit():
        print('validate add_shows')
        show_to_add = Show(show_name=form.show_name.data,
                           show_dir=form.show_dir.data,
                           watching=form.watching.data,
                           theTVDB_id=form.theTVDB_id.data,
                           theTVDB_name=form.theTVDB_name.data,
                           theTVDB_slug=form.theTVDB_slug.data,
                           theTVDB_status=form.theTVDB_status.data)
        print(show_to_add)
        db.session.add(show_to_add)
        new_show_added = NewShow.query.filter_by(new_show_id=form.new_show_id.data).first()
        print(new_show_added)
        if new_show_added:
            db.session.delete(new_show_added)
        db.session.commit()
        print(Show.query.all())
        print(NewShow.query.all())
        return redirect(url_for('add_shows'))
    return render_template('add_shows.html', title='Add TV Shows',
                           entries=entries, form=form)

@app.route('/list_shows', methods=['GET'])
def list_shows():
    '''
        in development
        page to list all show in db
    '''
    entries = []
    shows = Show.query.all()
    for show in sorted(shows, key=lambda s: s.show_name):
        entry = {}
        entry['show_id'] = show.show_id
        entry['show_name'] = show.show_name
        entry['show_dir'] = show.show_dir
        entry['watching'] = show.watching
        entry['theTVDB_id'] = show.theTVDB_id
        entries.append(entry)
    entries = sorted(entries, key=lambda e: e['show_name'])
    return render_template('list_shows.html', title='List TV Shows',
                           entries=entries)

@app.route('/episodes')
def episodes():
    '''
        in development
        page to process downloaded tv show episodes
    '''
    texts = []
    texts.append(API.search_series_params())
    texts.append(API.search_series('Rick and Morty'))
    texts.append(API.series(75978))
    return render_template('episodes.html', title='Episodes', texts=texts)


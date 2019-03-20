'''
    models.py
'''

from mediamgr import db

class Show(db.Model):
    '''
        table for TV Shows
    '''
    show_id = db.Column(db.Integer, primary_key=True)
    show_name = db.Column(db.String(64), index=True)
    show_dir = db.Column(db.String(64), index=True, unique=True)
    watching = db.Column(db.Boolean, unique=False, default=True)
    theTVDB_id = db.Column(db.Integer, index=True, unique=True)
    theTVDB_name = db.Column(db.String(64), index=True)
    theTVDB_slug = db.Column(db.String(64), index=True)
    theTVDB_status = db.Column(db.String(64), index=True)
    seasons = db.relationship('Season', backref='show', lazy='dynamic')

    def __repr__(self):
        return '<Show {} ({})>'.format(self.show_name, self.show_id)

class Show_Alias(db.Model):
    '''
        table for TV Shows Title Aliases
    '''
    alias_id = db.Column(db.Integer, primary_key=True)
    alias_name = db.Column(db.String(64), index=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'))

    def __repr__(self):
        return '<Alias {} ({}, {})>'.format(self.alias_name, self.alias_id, self.show_id)

class Season(db.Model):
    '''
        table for TV Shows Seasons
    '''
    season_id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, index=True, unique=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.show_id'))
    episodes = db.relationship('Episode', backref='season', lazy='dynamic')

    def __repr__(self):
        return '<Season {} ({}, {})>'.format(self.season, self.season_id, self.show_id)

class Episode(db.Model):
    '''
        table for TV Shows Episodes
    '''
    episode_id = db.Column(db.Integer, primary_key=True)
    episode = db.Column(db.Integer, index=True, unique=False)
    downloaded = db.Column(db.Boolean, unique=False, default=False)
    season_id = db.Column(db.Integer, db.ForeignKey('season.season_id'))
    theTVDB_id = db.Column(db.Integer, index=True, unique=True)
    theTVDB_name = db.Column(db.String(64), index=True)
    air_date = db.Column(db.String(64), index=True, unique=False)

    def __repr__(self):
        return '<Episode {} ({}, {})>'.format(self.episode, self.episode_id, self.season_id)

class NewShow(db.Model):
    '''
        table for New TV Shows
    '''
    new_show_id = db.Column(db.Integer, primary_key=True)
    new_show_name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<NewShow {} ({})>'.format(self.new_show_name, self.new_show_id)

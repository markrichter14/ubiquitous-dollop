import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or ''

    '''
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['your-email@example.com']
    '''


    BASE_DIR = ''
    MOVIE_DIR = BASE_DIR + '01_Movies/'
    MOVIE_DEST = BASE_DIR + '01_Movies_Move/'
    TV_DIR = BASE_DIR + '01_TV/'
    TV_DEST = BASE_DIR + '01_TV_Move/'

    THETVDB = {
        'BASE_URL' : 'https://api.thetvdb.com',
        'USERNAME' : '',
        'UNIQUE_ID' : '',
        'API_KEY' : '',
        'TOKEN' : '',
    }

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                                'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


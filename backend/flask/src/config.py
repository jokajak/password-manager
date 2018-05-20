import os
basedir = os.path.abspath(os.path.dirname(__file__))

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

ADMINS = ['you@example.com']

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    DEBUG = True
    # log all the statements issued to stderr
    SQLALCHEMY_ECHO = True
    # Enables get_debug_queries
    SQLALCHEMY_RECORD_QUERIES = True


class Testing(Config):
    TESTING = True


class Production(Config):
    DEBUG = False
    TESTING = False



config = {
    'development': Development,
    'testing': Testing,
    'production': Production,
}

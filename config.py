WTF_CSRF_ENABLED = True
SECRET_KEY = 'santa-clause-does-exist'


import os
basedir = os.path.abspath(os.path.dirname(__file__))

#The SQLALCHEMY_DATABASE_URI is required by the Flask-SQLAlchemy extension. 
#This is the path of our database file.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = True

# pagination
POSTS_PER_PAGE = 3

#full text search
WHOOSH_BASE = os.path.join(basedir, 'search.db')
MAX_SEARCH_RESULTS = 50

#email 
# email server
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# administrator list
ADMINS = ['justformytutorial@gmail.com']

# -*- coding: utf-8 -*-
# available languages
LANGUAGES = {
    'en': 'English',
}

# microsoft translation service
MS_TRANSLATOR_CLIENT_ID = '' # enter your MS translator app id here
MS_TRANSLATOR_CLIENT_SECRET = '' # enter your MS translator app secret here


# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None





















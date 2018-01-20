from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_babel import Babel, lazy_gettext

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)

#for sign up
from flask import Flask, request, render_template, redirect, url_for
from .forms import SignupForm

#for log in
import os
from flask_login import LoginManager

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login' #tells Flask_Login to go to login.html
lm.login_message = lazy_gettext('Please log in to access this page.')

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

if not app.debug:
    import logging

    #sending email
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    #putting this into log file
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')

#for time displayment
from .momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs

#for Internationalization and Localization (I18n and L10n)
babel = Babel(app)

from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)

app.json_encoder = CustomJSONEncoder

from app import views, models













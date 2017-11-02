from app import db
from hashlib import md5
import re

followers = db.Table('followers',
    db.Column('follower_nickname', db.String(64), db.ForeignKey('user.nickname')),
    db.Column('followed_nickname', db.String(64), db.ForeignKey('user.nickname'))
)

class User(db.Model):
    email = db.Column(db.String(80), primary_key=True, unique=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(80))
    #"one" side in one to many relationship
    #first argument is the "many" side
    #beckref means the "one" side
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime)
    followed = db.relationship('User', 
                               secondary=followers, 
                               primaryjoin=(followers.c.follower_nickname == nickname), 
                               secondaryjoin=(followers.c.followed_nickname == nickname), 
                               backref=db.backref('followers', lazy='dynamic'), 
                               lazy='dynamic')


    def __init__(self, email, password, nickname):
        self.email = email
        self.password = password
        self.nickname = nickname

    #for user login
    @property
    def is_authenticated(self): 
        return True #True unless the user is not allowed to authenticate

    @property
    def is_active(self):
        return True #True unless the user is inactive (e.g. banned)

    @property
    def is_anonymous(self):
        return False #False unless the user is is not supposed to log in to the system (e.g. fake users)

    def get_id(self):
        try:
            return unicode(self.email)  # python 2
        except NameError:
            return str(self.email)  # python 3

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    @staticmethod
    def make_valid_nickname(nickname):
        return re.sub('[^a-zA-Z0-9_\.]', '', nickname)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_nickname == user.nickname).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_nickname == Post.user_id)).filter(followers.c.follower_nickname == self.nickname).order_by(Post.timestamp.desc())

    def __repr__(self): #__repr__ is the method that specifies how to print objects of this class
        return '<User %r>' % (self.email)

#import sys
#if sys.version_info >= (3, 0):
#    enable_search = False
#else:
#    enable_search = True
#    import flask_whooshalchemy as whooshalchemy

class Post(db.Model):
    __searchable__ = ['body']

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.nickname'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post %r>' % (self.body)

from app import app
import flask_whooshalchemy as whooshalchemy
#if enable_search:
whooshalchemy.whoosh_index(app, Post)
















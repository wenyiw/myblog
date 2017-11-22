from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from .forms import SignupForm, EditForm, PostForm, SearchForm
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE
from .emails import follower_notification
from flask_babel import gettext #for translation
from app import babel
from config import LANGUAGES
from guess_language import guessLanguage

#for user login
#loads a user from database
@lm.user_loader #decorator
def load_user(email):
    return User.query.filter_by(email = email).first()

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()
    g.locale = get_locale()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if request.method == 'GET':
        return render_template('signup.html', form = form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            if User.query.filter_by(email=form.email.data).first():
                flash(gettext("Email address already exists"))
                return redirect(url_for('login'))
            else:
                nickname = form.email.data.split('@')[0]
                nickname = User.make_valid_nickname(nickname)
                nickname = User.make_unique_nickname(nickname)
                newuser = User(form.email.data, form.password.data, nickname)
                db.session.add(newuser) 
                db.session.commit()
                # make the user follow him/herself
                db.session.add(newuser.follow(newuser))
                db.session.commit()

                remember_me = False
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)

            login_user(newuser, remember = remember_me)

            flash(gettext("User Created!"))
            return redirect(url_for('index'))
        else:
            flash(gettext('Invalid form. Please try again.'))
            return redirect(url_for('signup'))

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required #make sure this page is only seen by logged in users
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, 
                    timestamp=datetime.utcnow(), 
                    author=g.user, 
                    language=language)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        
        #avoids submitting duplicate posts 
        #when users adverdently refresh the page after submitting a blog post
        return redirect(url_for('index'))
    
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    
    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts)

#methods tells Flask that this view function accepts GET and POST requests 
#without this only GET will be accepted
#POST is needed for bringing in the form data entered by the user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))

    form = SignupForm()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            user=User.query.filter_by(email=form.email.data).first()
            if user:
                if user.password == form.password.data:
                    login_user(user)
                    flash(gettext("User logged in"))
                    return redirect(url_for('index'))                
                else:
                    flash(gettext("Wrong password"))
                    return redirect(url_for('login'))            
            else:
                flash(gettext("User doesn't exist, please sign up"))
                return redirect(url_for('signup'))        
        else:
            flash(gettext("form not validated"))
            return redirect(url_for('login'))  

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %s not found.' % nickname))
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash(gettext('Your changes have been saved.'))
        return redirect(url_for('user', nickname=g.user.nickname))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
        flash(gettext('Invalid input'))
    return render_template('edit.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %s not found.' % nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t follow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash(gettext('Cannot follow ' + nickname + '.'))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You are now following ' + nickname + '!'))
    return redirect(url_for('user', nickname=nickname))
    follower_notification(user, g.user)
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash(gettext('User %s not found.' % nickname))
        return redirect(url_for('index'))
    if user == g.user:
        flash(gettext('You can\'t unfollow yourself!'))
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash(gettext('Cannot unfollow ' + nickname + '.'))
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash(gettext('You have stopped following ' + nickname + '.'))
    return redirect(url_for('user', nickname=nickname))


@app.route('/search', methods=['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search_results', query=g.search_form.search.data))

from config import MAX_SEARCH_RESULTS

@app.route('/search_results/<query>')
@login_required
def search_results(query):
    results = Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search_results.html',
                           query=query,
                           results=results)

from flask import jsonify
from .translate import microsoft_translate

@app.route('/translate', methods=['POST'])
@login_required
def translate():
    return jsonify({ 
        'text': microsoft_translate(
            request.form['text'], 
            request.form['sourceLang'], 
            request.form['destLang']) })













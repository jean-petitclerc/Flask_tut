from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, g
from flask_bootstrap import Bootstrap
from flask_script import Manager
from contextlib import closing
import sqlite3

app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)

# This creates the database connection for each request
@app.before_request
def before_request():
    g.db = connect_db()

# This close the db connection at the end of the requests
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

# Custom error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500

# The following functions are views
@app.route('/')
def index():
    app.logger.debug('Entering index()')
    user = session.get('username', None)
    return render_template('photos.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    # The method is GET when the form is displayed and POST to process the form
    app.logger.debug('Entering login()')
    if request.method == 'POST':
        if db_validate_user(request.form['username'], ' '):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid user name!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    app.logger.debug('Entering logout()')
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/list_dates')
def list_dates():
    cur = g.db.execute('select distinct photo_date from tphoto order by photo_date')
    photo_dates = [dict(photo_date=row[0]) for row in cur.fetchall()]
    app.logger.debug(photo_dates[0]['photo_date'])
    return render_template('list_dates.html', photo_dates=photo_dates)

@app.route('/list_photos_by_date/<p_date>')
def list_photos_by_date(p_date):
    app.logger.debug('Query photos for: ' + p_date)
    cur = g.db.execute('select photo_name from tphoto order by photo_name')
    list_photos = [dict(photo_name=row[0]) for row in cur.fetchall()]
    return render_template('list_photos.html', list_photos=list_photos)

# Database functions

# Connect to the database and return a db handle
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# Utility function to create the database from the schema definition in db.sql
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('data/db.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Execute a query
def db_query(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# Validate if a user is defined in tuser with the proper password.
def db_validate_user(user_name, user_pass):
    user = db_query('select user_name from tuser where user_name = ? and user_pass = ?',
                    [user_name, user_pass], one=True)
    if user is None:
        return False
    else:
        return True    

# Read the configurations
app.config.from_pyfile('config/photos.cfg')

# Start the server for the application
if __name__ == '__main__':
    manager.run()

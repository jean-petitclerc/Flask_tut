from flask import Flask, session, redirect, url_for, escape, request, render_template, flash, g
from contextlib import closing
import sqlite3

app = Flask(__name__)

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

# The following functions are views
@app.route('/')
def index():
    app.logger.debug('Entering index()')
    user = session.get('username', None)
    return render_template('my_app.html', user=user)

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
app.config.from_pyfile('config/my_app.cfg')

# Start the server for the application
if __name__ == '__main__':
    app.run()

from flask import Flask, session, redirect, url_for, escape, request, render_template, flash

app = Flask(__name__)

@app.route('/')
def index():
    user = session.get('username', None)
    return render_template('my_app.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid user name!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

app.config.from_pyfile('config/my_app.cfg')
app.run()

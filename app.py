from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fitformai-secret-change-in-production')

# Credentials via environment variables (set ADMIN_USER and ADMIN_PASS on your server)
USERS = {
    os.environ.get('ADMIN_USER', 'admin'): os.environ.get('ADMIN_PASS', 'admin123')
}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('home'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('home'))
        error = 'Invalid username or password.'
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/')
@login_required
def home():
    return render_template('index.html')


@app.route('/side_leg_raise')
@login_required
def side_leg_raise():
    return render_template('side_leg_raise.html')


@app.route('/plank')
@login_required
def plank():
    return render_template('plank.html')


@app.route('/squat')
@login_required
def squats():
    return render_template('squat.html')


@app.route('/bicep_curl')
@login_required
def bicep_curl():
    return render_template('bicep_curl.html')


if __name__ == '__main__':
    app.run(debug=False)

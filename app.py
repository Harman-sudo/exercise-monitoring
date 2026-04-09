import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/side_leg_raise')
def side_leg_raise():
    return render_template('side_leg_raise.html')


@app.route('/plank')
def plank():
    return render_template('plank.html')


@app.route('/squat')
def squats():
    return render_template('squat.html')


@app.route('/bicep_curl')
def bicep_curl():
    return render_template('bicep_curl.html')


@app.route('/testvideo/LEGRAISE.mp4')
def demo_legraise():
    video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'testvideo')
    return send_from_directory(video_dir, 'LEGRAISE.mp4')


if __name__ == '__main__':
    app.run(debug=False)

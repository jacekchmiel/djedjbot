import os

from flask import Flask, redirect, request, escape, url_for, session
import spotipy
import spotipy.util
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from spotipy import oauth2

SQLALCHEMY_TRACK_MODIFICATIONS = True

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://djedjbot:djedjbot_password@postgres/djedjbot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
ses = Session(app)

scope = 'user-library-read'


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('saved_tracks_page'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        get_spotify_oauth_token(session['username'])
        return redirect(url_for('index'))
    return '''
        <form method="post">
            User name
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''


@app.route('/saved_tracks')
def saved_tracks_page():
    token = get_spotify_oauth_token(session['username'])
    return get_saved_tracks(token)


class SpotifyUnauthorized(Exception):
    pass


def get_spotify_oauth_token(username, code=None):
    oauth = oauth2.SpotifyOAuth(os.getenv('SPOTIPY_CLIENT_ID'), os.getenv('SPOTIPY_CLIENT_SECRET'),
                                os.getenv('SPOTIPY_REDIRECT_URI'), scope=scope,
                                cache_path=".cache-" + username)
    if code:
        token_info = oauth.get_access_token(code)
        token = token_info['access_token']
    else:
        token_info = oauth.get_cached_token()
        if not token_info:
            raise SpotifyUnauthorized()
        token = token_info['access_token']

    return token


@app.route('/spotifylogin')
def spotify_login():
    code = request.args.get('code')
    return get_saved_tracks(get_spotify_oauth_token(session['username'], code))


def get_saved_tracks(token):
    rsp = []
    if token:
        sp = spotipy.Spotify(auth=token)
        offset = 0
        while True:
            results = sp.current_user_saved_tracks(offset=offset)
            for item in results['items']:
                track = item['track']
                rsp.append(track['name'] + ' - ' + track['artists'][0]['name'])

            if not results['items']:
                break

            offset += results['limit']

    else:
        print("Can't get token for", session['username'])
    return "<br>".join(rsp)

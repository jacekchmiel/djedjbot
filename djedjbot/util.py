import spotipy
from spotipy.util import prompt_for_user_token


def make_private_client(username):
    scopes = ['user-read-playback-state', 'user-read-currently-playing', 'playlist-read-private',
              'playlist-read-collaborative']
    # ['playlist-modify-private', 'playlist-modify-public', ]
    token = prompt_for_user_token(username, redirect_uri='http://localhost/', scope=' '.join(scopes))
    return spotipy.Spotify(auth=token)

from argparse import ArgumentParser

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.util import prompt_for_user_token
from datetime import timedelta


def make_client():
    try:
        client_credentials_manager = SpotifyClientCredentials()
    except SpotifyOauthError:
        print("Authorization Error. Provide SPOTIPY_APP_ID and SPOTIPY_APP_SECRET environment variables.")
        raise
    else:
        return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def make_private_client(username):
    scopes = ['user-read-playback-state', 'user-read-currently-playing', 'playlist-read-private',
              'playlist-read-collaborative']
    # ['playlist-modify-private', 'playlist-modify-public', ]
    token = prompt_for_user_token(username, redirect_uri='http://localhost/', scope=' '.join(scopes))
    return spotipy.Spotify(auth=token)


class PlaylistNotFound(Exception):
    pass


def get_playlist_by_name(spotify, playlist_name):
    playlists = spotify.current_user_playlists()
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            if playlist['name'] == playlist_name:
                return playlist
        if playlists['next']:
            playlists = spotify.next(playlists)
        else:
            playlists = None
    raise PlaylistNotFound(playlist_name)


def print_playlists(spotify):
    for i, playlist in enumerate(all_items(spotify, spotify.current_user_playlists())):
        print("%4d %s %s" % (i + 1, playlist['uri'], playlist['name']))


def all_items(spotify, first_call_result):
    result = first_call_result
    while result:
        for item in result['items']:
            yield item
        if result['next']:
            result = spotify.next(result)
        else:
            result = None


def get_playlist_tracks(spotify, user, playlist):
    if isinstance(playlist, str):
        playlist_id = playlist
    else:
        playlist_id = playlist['id']
    return [t['track'] for t in all_items(spotify, spotify.user_playlist_tracks(user, playlist_id))]


def get_tracks_features(spotify, tracks):
    if all(isinstance(t, str) for t in tracks):
        track_ids = tracks
    else:
        track_ids = [t['id'] for t in tracks]
    return spotify.audio_features(track_ids)


def parse_args():
    p = ArgumentParser()
    p.add_argument('-u', '--user', required=True)
    p.add_argument('-p', '--playlist', required=True)
    return p.parse_args()


def main():
    args = parse_args()
    sp = make_private_client(args.user)
    playlist = get_playlist_by_name(sp, args.playlist)
    tracks = get_playlist_tracks(sp, args.user, playlist)
    features = get_tracks_features(sp, tracks)
    time = timedelta(seconds=0)
    for i, (t, f) in enumerate(zip(tracks, features)):
        idx = i + 1
        name = t['name']
        duration = timedelta(seconds=t['duration_ms'] // 1000)
        time += duration
        tempo = int(f['tempo'])
        print('{idx:3}. {name:32.32} {tempo:3}  {duration}    {time}'.format(**locals()))


if __name__ == '__main__':
    main()

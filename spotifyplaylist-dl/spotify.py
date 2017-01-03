"""
Does the spotify bit.

Get playlist name, tracks and authentication
"""

import os
import base64

import requests

CLIENT_ID = os.environ.get('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SPOTIFY_CLIENT_SECRET')


def get_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    concat = client_id + ':' + client_secret
    authorization = base64.b64encode(concat.encode('ascii')).decode('ascii')
    data = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization': 'Basic ' + authorization
    }
    resp = requests.post(
        'https://accounts.spotify.com/api/token', headers=headers, data=data)
    access_token_response = resp.json()
    return access_token_response['access_token']


def get_playlist_name(user, playlist, token):
    spotify_api_url = 'https://api.spotify.com/v1/users/{}/playlists/{}'.format(
        user, playlist)
    resp = requests.get(
        spotify_api_url,
        headers={'Accept': 'application/json', 'Authorization': 'Bearer ' + token})
    return resp.json()['name']


def get_playlist_tracks(user, playlist, token):
    """
    Returns the track objects as seen in the spotify documentation
    https://developer.spotify.com/web-api/object-model/#track-object-full
    """
    songs = []
    spotify_api_url = 'https://api.spotify.com/v1/users/{}/playlists/{}/tracks'.format(
        user, playlist)
    while spotify_api_url:
        resp = requests.get(
            spotify_api_url,
            headers={'Accept': 'application/json', 'Authorization': 'Bearer ' + token})
        jsonout = resp.json()
        for item in jsonout['items']:
            songs.append(
                {
                    'title': item['track']['name'],
                    'artists': [a['name'] for a in item['track']['artists']]
                })
        spotify_api_url = jsonout.get('next', '')
    return songs


def parse_playlist_uri(uri):
    """
    Takes a playlist uri and splits it to (user_id, playlist_id)
    """
    playlistparts = uri.split(':')
    # Sample: spotify:user:lmljoe:playlist:0DXoY83tBvgWkd8QH49yAI
    if len(playlistparts) != 5:
        print('Invalid playlist id')
        exit()
    user_id = playlistparts[2]
    playlist_id = playlistparts[4]
    return user_id, playlist_id

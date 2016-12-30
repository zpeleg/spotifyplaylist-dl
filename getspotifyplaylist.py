"""
Downloads spotify playlists by searching for them on youtube.

TODO:
* Add argument parsing
  [V] Parse Spotify Playlist URI
  [V] Parse output folder, with sane default (./output/playlistname)
    [ ] Read playlist name
* Use youtube-dl as a function and not as a process
  * https://github.com/rg3/youtube-dl/blob/master/README.md#embedding-youtube-dl
"""

import base64
import json
import subprocess
import sys
import argparse
import os

import requests
from googleapiclient.discovery import build

with open("secrets.json") as secretsfile:
    SECRETS = json.load(secretsfile)

DEVELOPER_KEY = SECRETS["youtube"]["developerKey"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def __youtube_search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    # pylint: disable=maybe-no-member
    search_response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=25
    ).execute()

    videos = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append((search_result["snippet"]["title"], search_result["id"]["videoId"]))
    return videos

#youtube_search('gravity john mayer')


CLIENT_ID = SECRETS["spotify"]["clientId"]
CLIENT_SECRET = SECRETS["spotify"]["clientSecret"]

def __spotify_get_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
    concat = client_id+':'+client_secret
    authorization = base64.b64encode(concat.encode('ascii')).decode('ascii')
    data = {
        'grant_type': 'client_credentials'
    }
    headers = {
        'Authorization':'Basic ' + authorization
    }
    resp = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    access_token_response = resp.json()
    return access_token_response['access_token']


def __uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    """
    Print unicode strings to the console.

    Code from http://stackoverflow.com/a/29988426/365408
    """
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def __spotify_get_playlist_tracks(user, playlist, token):
    songs = []
    spotify_api_url = "https://api.spotify.com/v1/users/%s/playlists/%s/tracks" %(user, playlist)
    while spotify_api_url:
        resp = requests.get(
            spotify_api_url,
            headers={'Accept': 'application/json', 'Authorization': 'Bearer ' + token})
        jsonout = resp.json()
        for item in jsonout['items']:
            songs.append(
                {
                    'title':item['track']['name'],
                    'artists':[a['name'] for a in item['track']['artists']]
                })
        spotify_api_url = jsonout.get('next', '')
    return songs

def __get_youtubedl_command(artist, title, youtube_link,output_folder):
    return 'youtube-dl -o "{{outputfolder}}\\{{artist}} - {{title}} (%(title)s).%(ext)s" -w -q -x --audio-format best --audio-quality 0 -k --prefer-ffmpeg {{youtube_link}}' \
            .replace('{{artist}}', artist)\
            .replace('{{title}}', title)\
            .replace('{{youtube_link}}', youtube_link)\
            .replace('{{outputfolder}}', output_folder)

def __create_youtube_search_terms(songs):
    searchterms = []
    for song in songs:
        # If there are multiple artists for a song, try with all of them
        # This could download the same track multiple times, but they will overwrite themselves
        for artist_name in song['artists']:
            searchterms.append((song, '%s %s' % (song['title'], artist_name)))
    return searchterms

def __parse_playlist_uri(uri):
    playlistparts = uri.split(':')
    # Sample: spotify:user:lmljoe:playlist:0DXoY83tBvgWkd8QH49yAI
    if len(playlistparts) != 5:
        print("Invalid playlist id")
        exit()
    user_id = playlistparts[2]
    playlist_id = playlistparts[4]
    return user_id, playlist_id

def __main(playlist, output_folder, simulate_mode):
    user_id, playlist_id = __parse_playlist_uri(playlist)

    spotify_access_token = __spotify_get_access_token()
    print(' * Got access token')
    songs = __spotify_get_playlist_tracks(user_id, playlist_id, spotify_access_token)
    print(' * Got song list')

    searchterms = __create_youtube_search_terms(songs)

    for index, (song, term) in enumerate(searchterms):
        search_result = __youtube_search(term)
        __uprint(' * %i/%i %s - %s' % (index, len(searchterms), song['title'], str(song['artists'])))
        __uprint('   downloading: %s' % (str(search_result[0])))
        if not simulate_mode:
            command = __get_youtubedl_command(song['artists'][0], song['title'], search_result[0][1], output_folder)
            dl_process = subprocess.Popen(command)
            dl_process.communicate()

if __name__ == '__main__':
    # pylint: disable=C0103
    parser = argparse.ArgumentParser()
    parser.add_argument('playlist', help='Spotify uri of the playlist')
    parser.add_argument('-o', '--out', help='output folder', default='.\\output')
    parser.add_argument('-s', '--simulate', help='Do not download files, simulate process', action='store_true')
    args = parser.parse_args()
    print('Downloading playlist: {}\nSaving to {}'.format(args.playlist, os.path.abspath(args.out)))
    if args.simulate:
        print('XXX - running in simulate mode')
    __main(args.playlist, args.out, args.simulate)

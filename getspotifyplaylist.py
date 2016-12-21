"""Downloads spotify playlists by searching for them on youtube."""

import base64
import json
import subprocess
import sys

import requests
from googleapiclient.discovery import build

with open("secrets.json") as secretsfile:
    SECRETS = json.load(secretsfile)
    print(SECRETS)
print(sys.stdout.encoding)

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

def __get_access_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
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

    Code from:
    http://stackoverflow.com/a/29988426/365408
    """
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def __get_playlist_tracks(user, playlist, token):
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

def __main():
    access_token = __get_access_token()
    print(' * Got access token')
    songs = __get_playlist_tracks('oocdiddy', '2cjySDOU0ikjqjBa7JDgaV', access_token)
    print(' * Got song list')

    searchterms = []
    for song in songs:
        for artist_name in song['artists']:
            searchterms.append((song, '%s %s' % (song['title'], artist_name)))
    index = 0
    for item, term in searchterms:
        __uprint(term)
        search_result = __youtube_search(term)
        __uprint(' * %i/%i' % (index, len(searchterms)))
        __uprint('\t  %s - %s' % (item['title'], str(item['artists'])))
        __uprint('\t  downloading: %s' % (str(search_result[0])))
        command = 'youtube-dl -o "c:\\tmp\\songs\\{{artist}} - {{title}} (%(title)s).%(ext)s" -w -q -x --audio-format best --audio-quality 0 -k --prefer-ffmpeg ' \
            .replace('{{artist}}', item['artists'][0])\
            .replace('{{title}}', item['title'])\
            +search_result[0][1]
        index += 1
        dl_process = subprocess.Popen(command)
        dl_process.communicate()
        #uprint(command)

if __name__ == '__main__':
    __main()

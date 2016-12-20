from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import requests
import subprocess
import json
import codecs
import base64
import sys
import json

with open("secrets.json") as f:
	secrets = json.load(f)
	print(secrets)
print(sys.stdout.encoding)

DEVELOPER_KEY = secrets["youtube"]["developerKey"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(query):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    developerKey=DEVELOPER_KEY)

  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=query,
    part="id,snippet",
    maxResults=25
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      videos.append((search_result["snippet"]["title"],
                     search_result["id"]["videoId"]))
  return videos

#youtube_search('gravity john mayer')


CLIENT_ID = secrets["spotify"]["clientId"]
CLIENT_SECRET = secrets["spotify"]["clientSecret"]

def get_access_token(client_id=CLIENT_ID,client_secret=CLIENT_SECRET):
	concat = client_id+':'+client_secret
	authorization = base64.b64encode(concat.encode('ascii')).decode('ascii')
	data = {
		'grant_type': 'client_credentials'
	}
	headers={
		'Authorization':'Basic ' + authorization
	}
	resp = requests.post('https://accounts.spotify.com/api/token',headers=headers,data=data)
	js = resp.json()
	return js['access_token']

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)

def get_playlist_tracks(user, playlist, token):
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
		spotify_api_url = jsonout.get('next','')
	return songs

access_token = get_access_token()
print(' * Got access token')
songs = get_playlist_tracks('oocdiddy','2cjySDOU0ikjqjBa7JDgaV', access_token)
print(' * Got song list')

searchterms = []
for s in songs:
	for a in s['artists']:
		searchterms.append((s, '%s %s'%(s['title'],a)))
index = 0
for item, term in searchterms:
	uprint(term)
	search_result = youtube_search(term)
	uprint(' * %i/%i'%(index,len(searchterms)))
	uprint('\t  %s - %s'%(item['title'],str(item['artists'])))
	uprint('\t  downloading: %s' % (str(search_result[0])))
	command = 'youtube-dl -o "c:\\tmp\\songs\\{{artist}} - {{title}} (%(title)s).%(ext)s" -w -q -x --audio-format best --audio-quality 0 -k --prefer-ffmpeg ' \
		.replace('{{artist}}',item['artists'][0])\
		.replace('{{title}}',item['title'])\
		+search_result[0][1]
	index+=1
	p = subprocess.Popen(command)
	p.communicate()
	#uprint(command)

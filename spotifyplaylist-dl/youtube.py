"""
Does youtube functionality.

Including search using the api and downloading using youtube-dl
"""


import os

from googleapiclient.discovery import build
import progressbar
import youtube_dl


DEVELOPER_KEY = os.environ.get('YOUTUBE_DEVELOPER_KEY')
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'


def search(query):
    youtube = build(YOUTUBE_API_SERVICE_NAME,
                    YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified
    # query term.
    # pylint: disable=maybe-no-member
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=25
    ).execute()

    videos = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            videos.append((search_result['snippet'][
                          'title'], search_result['id']['videoId']))
    return videos


def create_search_terms(songs):
    searchterms = []
    for song in songs:
        # If there are multiple artists for a song, try with all of them
        # This could download the same track multiple times, but they will
        # overwrite themselves
        for artist_name in song['artists']:
            searchterms.append(
                (song, '{} {}'.format(song['title'], artist_name)))
    return searchterms


def __sanitize_file_name(name):
    return name.replace('/', '_').replace('\\', '_')


def youtube_download_audio(song, youtube_id, output_folder, audio_qaulity):
    progress = progressbar.ProgressBar()
    progress.start()

    def progress_callback(data):
        if data['status'] != 'downloading' or 'downloaded_bytes' not in data or 'total_bytes' not in data:
            return
        progress.update(data['downloaded_bytes'] / data['total_bytes'] * 100)
        # print('total bytes: {}. downloaded: {}. result: {}'.format(data['total_bytes'],data['downloaded_bytes'],))
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': str(audio_qaulity),
        }],
        'outtmpl': '{}\\{} - {} (%(title)s).%(ext)s'.format(
            output_folder,
            __sanitize_file_name(','.join(song['artists'])),
            __sanitize_file_name(song['title'])),
        'nooverwrites': True,
        'quiet': True,
        'progress_hooks': [progress_callback]
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_id])
    progress.finish()

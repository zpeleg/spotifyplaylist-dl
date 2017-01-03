"""
Downloads spotify playlists by searching for them on youtube.
"""

import sys
import argparse
import os
from os.path import dirname, realpath, join

from dotenv import load_dotenv

load_dotenv(join(dirname(realpath(__file__)), '.env'))

import youtube
import spotify

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

def download_playlist(playlist, output_folder, simulate_mode, audio_quality):
    """
    Downloads the given playlist into output_folder.

    You should make sure that the environment variables for the spotify
    and youtube module are set with valid keys and secrets.
    """
    user_id, playlist_id = spotify.parse_playlist_uri(playlist)

    spotify_access_token = spotify.get_access_token()
    print(' * Got access token')
    playlist_name = spotify.get_playlist_name(user_id, playlist_id, spotify_access_token)
    print(' * Playlist name: "{}"'.format(playlist_name))
    songs = spotify.get_playlist_tracks(user_id, playlist_id, spotify_access_token)
    print(' * Got song list - {} songs'.format(len(songs)))

    searchterms = youtube.create_search_terms(songs)

    for index, (song, term) in enumerate(searchterms):
        search_result = youtube.search(term)
        if not search_result:
            __uprint('   XXX - could not find {}'.format(song['title']))
            continue
        __uprint(' * {}/{} {} - {}'.format(index, len(searchterms), ', '.join(song['artists']), song['title']))
        __uprint('   downloading: {}'.format(search_result[0]))
        if not simulate_mode:
            youtube.youtube_download_audio(song, search_result[0][1], output_folder, audio_quality)

if __name__ == '__main__':
    # pylint: disable=C0103
    parser = argparse.ArgumentParser()
    parser.add_argument('playlist', help='Spotify uri of the playlist')
    parser.add_argument('-o', '--out', help='output folder', default='.\\output')
    parser.add_argument('-s', '--simulate', help='Do not download files, simulate process', action='store_true')
    parser.add_argument('-q', '--quality', help='Encoding quality of mp3. Can be a bitrate or 0-9 for vbr', default=192)
    args = parser.parse_args()
    print('Downloading playlist: {}\nSaving to {}\nUsing quality {}'.format(args.playlist, os.path.abspath(args.out), args.quality))
    if args.simulate:
        print('XXX - running in simulate mode')
    print('\n')
    download_playlist(args.playlist, args.out, args.simulate, args.quality)

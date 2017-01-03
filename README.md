# SpotifyPlaylist-dl

This project is a command line utility for downloading spotify playlists. It does so by looking up each of the songs on youtube and downloading the audio using `youtube-dl`.

## Getting started

* Clone this repository
* Run `pip install -r requirements.txt` to install the requirements
* Acquire API keys for  [spotify](https://developer.spotify.com/my-applications/#!/applications) and [youtube](https://developers.google.com/youtube/android/player/register)
* Set the api keys either as environment variables as seen in `.env.example` or rename `.env.example` to `.env` and put your keys in the appropriate places.


## Usage

```
python spotifyplaylist-dl.py spotify:user:zpeleg:playlist:7MpgGne028tIFZ5XnWa2LL
```

The playlist uri can be copied by going to the playlist, clicking the three dots button next to the play button and choosing "Copy Spotify URI".

### Additional options

	usage: spotifyplaylist-dl.py [-h] [-o OUT] [-s] [-q QUALITY] playlist
	
	positional arguments:
	  playlist              Spotify uri of the playlist
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -o OUT, --out OUT     output folder
	  -s, --simulate        Do not download files, simulate process
	  -q QUALITY, --quality QUALITY
	                        Encoding quality of mp3. Can be a bitrate or 0-9 for
	                        vbr

#### --output / -o

Set a different output directory, default is to create a new directory within the current one called output\ and place all the files there.

#### --simulate / -s

Runs the script without actually downloading the files, useful to see that all the songs are picked up correctly and that the youtube search actually finds the right songs.

Note, that we are using youtube-dl, which downloads the video file and extracts the audio from it, so this will take some significant bandwith.

#### --quality / -q

This switch is passed directly to youtube-dl (which passes it to ffmpeg), specifing values above 10 will set a fixed bitrate of that value (for example 64, 192, 320). Otherwise, you can specify a number between 0-9 to choose vbr encoding quality (0 being highest quality and 9 being lowest).

## License

MIT
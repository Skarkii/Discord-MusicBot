# Discord-Bot

A music bot that just should work.

## Features
  * Play songs from any supported source
  * Skip songs
  * Pause songs
  * Display queue
  * Play playlists
  * Interactive messages in channel
  * Clear queue
  * Shuffle queued songs
  * Move songs in queue
  * Leave on inactivity

## Customizable
  * Prefix for commands
  * Timeout time

## Supported Sources
  * Youtube [Song & Playlist fully working]
  * Soundcloud [Song fully working, Playlist will play correctly with invalid title & duration in chat]
  * Spotify [Song & Playlist fully working]
  * Generally all supported formats from [yt-dlp - Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), though most untested.

## Example
To be added

## Setup
  * Python is required
  * [yt-dlp](https://github.com/yt-dlp/yt-dlp/) is required
  * [Discord.py](https://github.com/Rapptz/discord.py) is required
  * [ffmpeg](https://ffmpeg.org/) is required (both pip and standalone version)
  * [PyNaCl](https://pypi.org/project/PyNaCl/) is required
  * [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) is required

### Pip packages can installed with one command:
```sh
pip install -r requirements.txt
```
and standalone version of ffmpeg differs in different operating systems:


Apt-Get:
```sh
sudo apt-get install ffmpeg
```


Windows:
```ps1
winget install ffmpeg
```

Copy example_config.ini to config.ini, fill all fields in config.ini

Navigate to the bot folder, and run `python3 .`

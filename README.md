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

## To be implemented
  * Take turns queue
  * Leave on inactivity
  * Bind to text channel in server
  * Blacklist users from using the bot

## Customizable
  * Prefix for commands

## Supported Sources
  * Youtube [Song & Playlist fully working]
  * Soundcloud [Song fully working]
  * Spotify [Song & Playlist fully working]
  * Generally all supported formats from [yt-dlp - Supported Sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md), though most untested.

## Example
To be added

## Setup
  * Python is required
  * [yt-dlp](https://github.com/yt-dlp/yt-dlp/) is required
  * [Discord.py](https://github.com/Rapptz/discord.py) is required
  * [ffmpeg](https://ffmpeg.org/) is required
  * [PyNaCl](https://pypi.org/project/PyNaCl/) is required
  * [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) is required

### Can now be installed with a single command:
```sh
pip install -r requirements.txt
```

Copy example_config.ini to config.ini, fill all fields in config.ini

Navigate to the bot folder, and run `python3 .`.

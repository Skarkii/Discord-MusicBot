from config import config as config
import os
import time
import asyncio
import uuid
import json

# Youtube downloader
import yt_dlp

# Spotify API
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=config['SPOTIFY']['ID'], client_secret=config['SPOTIFY']['SECRET']))

async def get_all_playlist_items(sp, playlist_id):
    all_items = []
    offset = 0

    while True:
        results = sp.playlist_tracks(playlist_id, offset=offset)

        if not results['items']:
            break

        all_items.extend(results['items'])
        offset += len(results['items'])

    urls = []

    for song in all_items:
        urls.append({'url': song['track']['external_urls']['spotify'], 'name': song['track']['name'], 'artist': song['track']['artists'][0]['name'], 'duration': song['track']['duration_ms']/1000})

    return urls

async def get_single_song(sp, url):
    song = sp.track(url)
    return [{'url': song['external_urls']['spotify'], 'name': song['name'], 'artist': song['artists'][0]['name'], 'duration': song['duration_ms']/1000}]

async def spotify_appender(url):
    if("playlist" in url):
        return await get_all_playlist_items(sp, url)
    return await get_single_song(sp, url)

async def soundcloud_set_appender(url):
    return []

async def general_appender(playlist_url):
    url = []

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'ignoreerrors': True,
        'extract_flat': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)

            if(info is None):
                info = ydl.extract_info(f"ytsearch:{playlist_url}", download=False)

            print(info)

            if 'entries' in info:
                for entry in info['entries']:
                    url.append({'url': entry['url'],'name': entry['title'], 'artist': "", 'duration': entry['duration']})
            else:
                url.append({'url': info['url'], 'name': info['title'], 'artist': "", 'duration': info['duration']})

            return list(url)

    except yt_dlp.DownloadError as e:
        print(f'YT DLP Error: {e}')
        return []

class Song:
    def __init__(self, url, name="no-title",artist="", requested_by="Noone", duration=0):
        self.file_path = config['DISCORD']['SONGS_FOLDER']
        self.file_name = str(uuid.uuid4())
        self.full_path = self.file_path + self.file_name
        self.duration = duration
        self.name = name
        self.artist = artist
        self.is_ready = False
        self.requested_by = requested_by
        self.url = url

    async def spotify_to_youtube_url(self):
        ydl_opts = {
            'quiet': False,
            'ignoreerrors': True,
            'extract_flat': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{1}:{self.name} {self.artist}", download=False)

                return info['entries'][0]['url']

        except yt_dlp.DownloadError as e:
            print(f'YT DLP Error: {e}')
            return []

    async def get_playback_url(self):
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': False,
            'ignoreerrors': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                playback_url = info['url']
                print("info: -----:" , info)
                print(playback_url)
                return playback_url

        except yt_dlp.DownloadError as e:
            print(f'YT DLP Error: {e}')
            return []

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
    urls = []
    playlist = sp.playlist(playlist_id)

    for song in playlist['tracks']['items']:
        print(song)
        urls.append({'url': song['track']['external_urls']['spotify'], 'name': song['track']['name'], 'artist': song['track']['artists'][0]['name'], 'duration': song['track']['duration_ms']/1000})

    return urls

async def get_all_album_items(sp, album_id):
    urls = []
    album = sp.album(album_id)

    for song in album['tracks']['items']:
        urls.append({'url': song['external_urls']['spotify'], 'name': song['name'], 'artist': song['artists'][0]['name'], 'duration': song['duration_ms']/1000})

    return urls

async def get_single_song(sp, url):
    song = sp.track(url)
    return [{'url': song['external_urls']['spotify'], 'name': song['name'], 'artist': song['artists'][0]['name'], 'duration': song['duration_ms']/1000}]

async def spotify_appender(url):
    if("playlist" in url):
        return await get_all_playlist_items(sp, url)
    elif("album" in url):
        return await get_all_album_items(sp, url)
    return await get_single_song(sp, url)

async def soundcloud_set_appender(playlist_url):
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

            if 'entries' in info:
                for entry in info['entries']:
                    url.append({'url': entry['url'],'name': "noname", 'artist': "", 'duration': 0})
            else:
                pass
                url.append({'url': info['url'], 'name': info['title'], 'artist': "", 'duration': info['duration']})

            return list(url)
    except yt_dlp.DownloadError as e:
        print(f'YT DLP Error: {e}')
        return []

async def general_appender(playlist_url):
    url = []

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': False,
        'ignoreerrors': True,
        'extract_flat': 'in_playlist'
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
                url.append({'url': info['webpage_url'], 'name': info['title'], 'artist': "", 'duration': info['duration']})

            return list(url)

    except yt_dlp.DownloadError as e:
        print(f'YT DLP Error: {e}')
        return []

class Song:
    def __init__(self, url, name="no-title",artist="", requested_by="Noone", duration=0):
        self.duration = duration
        self.name = name
        self.artist = artist
        self.is_ready = False
        self.requested_by = requested_by
        self.url = url
        print("Added with url: " , self.url)

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

        if("spotify.com" in self.url):
            self.url = await self.spotify_to_youtube_url()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                return info['url']

        except yt_dlp.DownloadError as e:
            print(f'YT DLP Error: {e}')
            return []

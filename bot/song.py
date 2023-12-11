import yt_dlp
from config import config as config
import os
import time
import asyncio
import uuid
import json
from spotdl import *

spotdl = Spotdl(client_id=config['SPOTIFY']['ID'], client_secret=config['SPOTIFY']['SECRET'], no_cache=True)

async def is_playlist(playlist_url):
    if("spotify" in playlist_url):
        # Horrible fix, needs to be changed.
        song_info = spotdl.search([playlist_url])
        print("Song info : ", song_info[0])
        if(song_info[0].list_name is None):
            playlist_url = song_info[0].name + " " + song_info[0].artist
        else:
            url = []
            for i in range(song_info[0].list_length):
                url.append(await is_playlist(song_info[i].name + " " + song_info[i].artist))
            return [item for sublist in url for item in sublist]
        
    ydl_opts = {
        'quiet': False,
        'ignoreerrors': True,
        'extract_flat': "in_playlist",
        'default_search': 'ytsearch',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            print(info)
            url = []
            if 'entries' in info:
                for entry in info['entries']:
                    url.append({'url': entry['url'], 'name': entry['title']})
            else:
                url.append({'url': playlist_url, 'name': info['title']})
                return list(url)
            
            return list(url)

    except yt_dlp.DownloadError as e:
        print(f'YT DLP Error: {e}')
        return []
    
class Song:
    def __init__(self, url, name="no-title", requested_by="Noone"):
        self.file_path = config['DISCORD']['SONGS_FOLDER']
        self.file_name = str(uuid.uuid4())
        self.full_path = self.file_path + self.file_name
                
        self.name = name
        self.length = 0
        self.is_ready = False
        self.requested_by = requested_by
        self.url = url
        
    def __del__(self):
        try:
            #os.remove(self.full_path)
            pass
        except Exception as e:
            print(f"Error removing file: {e}")
        print("Song deleted")
    
    def ytdlp_download(self, url, output_path, file_name):
        options = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': f'{output_path}/{file_name}',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(f'{url}', download=True)

    async def download_video(self, url, path, name):
        try:
            loop = asyncio.get_event_loop()

            await loop.run_in_executor(None, self.ytdlp_download, url, path, name)
        except Exception as e:
            print(f'An error occurred: {e}')
            
    async def download(self):
        try:
            await self.download_video(self.url, self.file_path, self.file_name)
        except Exception as e:
            print("Youtube download failed", e)
        self.is_ready = True
        return True

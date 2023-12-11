import yt_dlp
from config import config as config
import os
import time
import asyncio
import uuid
import json

async def is_playlist(playlist_url):
    ydl_opts = {
        'quiet': False,
        'ignoreerrors': True,
        'extract_flat': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(playlist_url, download=False)
            url = []
            if 'entries' in info:
                for entry in info['entries']:
                    url.append(entry['url'])
            else:
                return [playlist_url]
            return url

    except yt_dlp.DownloadError as e:
        print(f'YT DLP Error: {e}')
        return []
    
class Song:
    def __init__(self, url, requested_by):
        self.file_path = config['DISCORD']['SONGS_FOLDER']
        self.file_name = str(uuid.uuid4())
        self.full_path = self.file_path + self.file_name
                
        self.name = "No-title"
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
            'default_search': 'ytsearch',
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info_dict = ydl.extract_info(f'{url}', download=True)
            self.name = info_dict['title']
        
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

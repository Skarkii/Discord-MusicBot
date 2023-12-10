import yt_dlp
import re
from config import config as config
import os
import time
import asyncio
import uuid


youtube_pattern = (
    r'(https?://)?(www\.)?'
    '(youtube|youtu|youtube-nocookie)\.(com|be|se)/'
    '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')


class Song:
    def __init__(self, url, requested_by):
        self.file_path = config['DISCORD']['SONGS_FOLDER']
        self.file_name = str(uuid.uuid4())
        self.name = "No-title"
        self.length = 0
        self.is_ready = False
        self.full_path = self.file_path + self.file_name
        self.requested_by = requested_by
        self.url = url
                
    def __del__(self):
        try:
            os.remove(self.full_path)
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
            info_dict = ydl.extract_info(url, download=True)
            self.name = info_dict.get('title', 'Unknown')
            self.length = info_dict.get('duration', 0)

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

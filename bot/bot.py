import discord
from config import config as config
from song import Song as Song
import time
import threading
import concurrent.futures
import asyncio
import requests
from voice import Voice as Voice

class Bot(discord.Client):
    def __init__(self, TOKEN, INTENTS):
        super().__init__(intents=INTENTS)
        self.TOKEN = TOKEN
        self.voice_connections = []
        self.song_queue = {}
        self.is_running = True
        self.version = 1.1
        self.run(self.TOKEN)


    # Thread to start playing songs
    async def play_task(self):
        await self.wait_until_ready()

        while not self.is_closed():
            await asyncio.sleep(0.5)
            for vc in self.voice_connections:
                if(len(vc.songs) > 0 and not vc.voice_client.is_playing() and not vc.is_paused):
                    s = vc.songs.pop(0)
                    await vc.start_playing(s)
                    del s

    async def check_version(self):
        if(config['DISCORD']['NOTIFY_NEW_VERSIONS'] == "False"):
            return

        try:
            response = requests.get("https://api.github.com/repos/skarkii/discord-musicbot/releases/latest", timeout=5)
        except requests.exceptions.Timeout:
            return

        v = response.json()["name"][1:]

        try:
            float(v)
        except ValueError:
            print("Failed to verify version from Github API, have naming convention changed?")
            return

        if(float(v) > self.version):
            msg = f"Version {v} is now available to download at https://github.com/Skarkii/Discord-MusicBot/releases !"
            print(msg)
            if(int(config['DISCORD']['OWNER_ID']) == 0):
                return
            u = await self.fetch_user(int(config['DISCORD']['OWNER_ID']))
            if u is not None:
                await u.send(msg)
            else:
                print("Could not fetch OWNER_ID to send new available version message")


    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        await self.check_version()
        self.loop.create_task(self.play_task())

    async def on_message(self, message):
        if(message.author.id == self.user.id):
            return

        v = None
        for vc in self.voice_connections:
            if vc.gid == message.guild.id:
                v = vc
                break

        if v is None:
            v = Voice(self, message.guild.id)
            self.voice_connections.append(v)

            if message.guild.id in self.song_queue:
                v.songs = self.song_queue[message.guild.id]

        await v.handle_message(message)

    async def on_voice_state_update(self, member, before, after):
        if(member == self.user):
            if before.channel and not after.channel:
                for vc in self.voice_connections:
                    if vc.gid == before.channel.guild.id:
                        print("I was kicked or disconnected")
                        self.song_queue[before.channel.guild.id] = vc.songs
                        await vc.on_kicked()
                        self.voice_connections.remove(vc)
                        break

            elif before.channel and after.channel and before.channel != after.channel:
                for vc in self.voice_connections:
                    if vc.voice_client.channel == after.channel:
                        print("I was moved")
                        await vc.on_move(after.channel)
                        break

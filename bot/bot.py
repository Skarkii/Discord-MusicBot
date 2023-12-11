import discord
from config import config as config
from song import Song as Song
import time
import threading
import concurrent.futures
import asyncio

from voice import Voice as Voice

class Bot(discord.Client):
    def __init__(self, TOKEN, INTENTS):
        super().__init__(intents=INTENTS)    
        self.TOKEN = TOKEN
        self.voice_connections = []
        self.is_running = True
    
        self.run(self.TOKEN)
        
    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        
        while(self.is_running == True):
            await asyncio.sleep(1)
            for vc in self.voice_connections:
                if(len(vc.songs) > 0 and vc.songs[0].is_ready and not vc.voice_client.is_playing() and not vc.is_paused):
                    s = vc.songs.pop(0)
                    await vc.start_playing(s)
                    print("Start playing songs!", s.url)
                    del s
                    
        await self.close()

    async def on_message(self, message):
        v = None
        for vc in self.voice_connections:
            if vc.gid == message.guild.id:
                v = vc
                break

        if v is None:
            v = Voice(self, message.guild.id)
            self.voice_connections.append(v)
            
        await v.handle_message(message)
    
    async def on_voice_state_update(self, member, before, after):
        if(member.bot):        
            if before.channel and not after.channel:
                for vc in self.voice_connections:
                    if vc.gid == before.channel.guild.id:
                        print("I was kicked")
                        await vc.on_kicked()
                        break

            if before.channel and after.channel and before.channel != after.channel:
                for vc in self.voice_connections:
                    if vc.voice_client.channel == after.channel:
                        print("I was moved")
                        await vc.on_move(after.channel)
                        break

            

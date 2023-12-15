import threading
import yt_dlp
import discord
import time
import asyncio
from song import Song as Song
from song import general_appender, spotify_appender
from config import config as config

class Voice():
    def __init__(self, bot, gid):
        print("Created voice bot")
        self.bot = bot
        self.gid = gid
        self.voice_client = None
        self.current_server = None
        self.is_running = True
        self.songs = []
        self.is_playing = False
        self.is_paused = False
        self.current = None
        self.prefix = config['MESSAGES']['PREFIX']

        self.channel = None #temp

    async def current_song(self):
        if(self.current is not None):
            song = self.current
            embed = discord.Embed(
                title=':headphones: Song Playing Now',
                description= f'[{song.name}]({song.url})',
                color=discord.Color.blue()
            )
            embed.add_field(name=f'**Requester:** {song.requested_by}', value='', inline=False)
            await self.channel.send(embed=embed)
            #await self.send_message(self.channel, ("Current song: " + self.current.name))
        
    def on_finished_play(self, song, error):
        print("Finished playing", song)
        self.current = None
        if error:
            print(f'An error occurred: {error}')

        self.is_playing = False
        
    async def start_playing(self, song):
        self.is_playing = True
        try:
            source = discord.FFmpegPCMAudio(source=song.full_path)
            self.current = song
            self.voice_client.play(source, after=lambda error: self.on_finished_play(song, error))
            embed = discord.Embed(
                title=':headphones: Song Playing Now',
                description= f'[{song.name}]({song.url})',
                color=discord.Color.blue()
            )
            embed.add_field(name=f'**Requester:** {song.requested_by}', value='', inline=False)
            await self.channel.send(embed=embed)
        except:
            pass
        
    async def display_help(self, channel):
        embed = discord.Embed(
            title='**Available Commands**',
            color=discord.Color.blue()
        )

        embed.add_field(name=f':headphones: `MUSIC`', value='', inline=False)
        embed.add_field(name=f'**play** - Plays a song', value='', inline=False)

        embed.add_field(name=f':satellite: `OTHER`', value='', inline=False)
        embed.add_field(name=f'**help** - display this message', value='', inline=False)
                    
        await self.channel.send(embed=embed)
        

    async def display_queue(self, channel):
        # Create an embed object
        if(len(self.songs) > 0):
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Queue length: {str(len(self.songs))} | Page Number: x/y | :hourglass: Duration: `{"duration"}`',
                color=discord.Color.blue()
            )

            i = 0
            for song in self.songs:
                i = i + 1
                if(i > 10):
                    break
                embed.add_field(name=f'', value=f'`{i}` **-** [{song.name}]({song.url}) - `{song.length}`', inline=False)
        else:
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Song queue is empty, use -play to play songs',
                color=discord.Color.blue()
            )
                    
        await self.channel.send(embed=embed)
        
    async def handle_message(self, message):
        if(message.author.bot == True):
            return
        self.channel = message.channel
        print(f'{message.author} said {message.content}')
        if(message.content == self.prefix + "join"):
            await self.join(message.author)

        if(message.content == self.prefix + "move"):
            await self.join(message.author, force=True)

        if(message.content == self.prefix + "help" or message.content == self.prefix + "commands"):
            await self.display_help(message.channel)

        if(message.content == "embed"):
            await self.embed(message.channel, "test")

        if(message.content == self.prefix + "c" or message.content == self.prefix + "current"):
            await self.current_song()

        if(message.content == self.prefix + "leave"):
            await self.leave()

        if(message.content == self.prefix + "sleep"):
            await self.send_message(message.channel, "Sleeping for five secounds")
            await self.long_task()
            await self.send_message(message.channel, "Finished sleeping!")

        if(message.content == "jo"):
            await self.send_message(message.channel, "jo")

        if((message.content.split(' ')[0] == self.prefix + "p" or message.content.split(' ')[0] == self.prefix + "play")):
            urls = None
            if(self.voice_client is None):
                await self.join(message.author)

            if("spotify" in ' '.join(message.content.split(' ')[1:])):
                 urls = await spotify_appender(' '.join(message.content.split(' ')[1:]))
            else:
                urls = await general_appender(' '.join(message.content.split(' ')[1:]))

            print(urls)
            for url in urls:
                print("URL :", url)
                s = Song(url['url'], url['name'], message.author)
                self.songs.append(s)
            #await message.add_reaction(':x:')
            await message.add_reaction('\u2705')
            print("ADDED ALL SONGS")
            return

        if(message.content.split(' ')[0] == self.prefix + "skip"):
            self.voice_client.stop()

        if(message.content == self.prefix + "pause"):
            if(self.is_paused):
                self.voice_client.resume()
                self.is_paused = False
            else:
                self.voice_client.pause()
                self.is_paused = True

        if(message.content == self.prefix + "queue" or message.content == self.prefix + "q"):
            await self.display_queue(message.channel)

        if(message.content == self.prefix + "skip"):
            self.voice_client.stop()
            # Create anmbed object with a clickable link
            embed = discord.Embed(
                title=':fast_forward: **Song Skipped**',
                color=discord.Color.blue()  # You can customize the color
            )

            # Send the embed to the same channel where the command was used
            await message.channel.send(embed=embed)

        if(message.content == self.prefix + "stop"):
            await self.leave()
            # Create an embed object with a clickable link
            embed = discord.Embed(
                title=':stop_button: **Player Stopped**',
                color=discord.Color.blue()  # You can customize the color
            )

            # Send the embed to the same channel where the command was used
            await message.channel.send(embed=embed)
            
    async def send_message(self, channel, msg):
        await channel.send(msg)
        
    async def join(self, author, force=False):
        channel = author.voice.channel

        if(channel == self.current_server):
            print("Already in that server")
            return
        
        if(self.voice_client is None):
            self.voice_client = await channel.connect(self_deaf=True)
            self.current_server = channel
        else:
            if(len(self.current_server.members) > 1 and force == False):
                #print("I'm connected in channel with other users, use -move to override")
                #return
                pass
            await self.voice_client.disconnect()
            self.voice_client = await channel.connect(self_deaf=True)
            self.current_server = channel

    async def leave(self):
        if(self.voice_client is not None):
            await self.voice_client.disconnect()
            for i in range(len(self.songs)):
                s = self.songs.pop()
                del s
        self.voice_client = None
        self.current_server = None

    async def on_kicked(self):
        await self.leave()

    async def on_move(self, new_channel):
        self.current_server = new_channel
        
        await self.voice_client.move_to(new_channel)

        if(not self.is_paused):
            await asyncio.sleep(0.5)
            self.voice_client.resume()

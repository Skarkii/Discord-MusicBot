import threading
import yt_dlp
import discord
import time
import asyncio
from random import shuffle
from song import Song as Song
from song import general_appender, spotify_appender, soundcloud_set_appender
from config import config as config
from users import *


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
        #self.users_path = config['DISCORD']['USERS_PATH']

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
        embed.add_field(name=f'**shuffle** - Shuffles the queue', value='', inline=False)
        embed.add_field(name=f'**queue** - Displays the queue', value='', inline=False)
        embed.add_field(name=f'**skip** - Skip the current song', value='', inline=False)
        embed.add_field(name=f'**clear** - Clears the queue', value='', inline=False)
        embed.add_field(name=f'**move X Y** - Moves song X to position Y', value='', inline=False)
        embed.add_field(name=f'**stop** - Stops playing and disconnects', value='', inline=False)

        embed.add_field(name=f':satellite: `OTHER`', value='', inline=False)
        embed.add_field(name=f'**stats(WIP)** - Displays stats about you', value='', inline=False)
        embed.add_field(name=f'**help** - display this message', value='', inline=False)

        await self.channel.send(embed=embed)

    async def get_total_duration(self):
        duration = 0
        for song in self.songs:
            duration = duration + song.duration
        return duration

    async def display_queue(self, channel):
        if(len(self.songs) > 0):
            total_duration = await self.get_total_duration()
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Queue length: {str(len(self.songs))} | Page Number: {(0//10)+1}/{(len(self.songs)//10)+1} | :hourglass: Duration: `{int(total_duration // 60)}:{str(int(total_duration % 60)).zfill(2)}`',
                color=discord.Color.blue()
            )

            i = 0
            for song in self.songs:
                i = i + 1
                if(i > 10):
                    break
                embed.add_field(name=f'', value=f'`{i}` **-** [{song.name}]({song.url}) - `{int(song.duration // 60)}:{str(int(song.duration % 60)).zfill(2)}`', inline=False)
        else:
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Song queue is empty, use {self.prefix}play to play songs',
                color=discord.Color.blue()
            )

        await self.channel.send(embed=embed)

    async def clear_queue(self, message):
        while(len(self.songs) > 0):
            s = self.songs.pop(0)
            del s
        await message.add_reaction('\u2705')

    async def shuffle_list(self, message):
        shuffle(self.songs)
        embed = None
        if(len(self.songs) > 0):
            embed = discord.Embed(
                title=f':notes: You successfully shuffled your {len(self.songs)} entries.',
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title=f":no_entry_sign: You don't have any music in the queue to shuffle!",
                color=discord.Color.blue()
            )


        await self.channel.send(embed=embed)

    async def move_song(self, ind1, ind2):
        #print(f"MOVE SONG {ind1} to {ind2}")
        ind1 = int(ind1)
        ind2 = int(ind2)

        if(ind1 <= 0 or ind1 > len(self.songs)):
            print(f"Invalid value: {ind1}")
            return

        if(ind2 <= 0 or ind1 > len(self.songs)):
            print(f"Invalid value: {ind2}")
            return

        s = self.songs.pop(ind1 - 1)
        self.songs.insert(ind2 - 1, s)
        print("Successfully moved song")
        return

    async def handle_message(self, message):
        if(message.author.bot == True):
            return

        if(message.content == "jo"):
            await self.send_message(message.channel, "jo")

        print(f'{message.author} said {message.content}')

        if(message.content[0] == self.prefix):
            self.channel = message.channel
        else:
            return

        if(message.content == self.prefix + "join"):
            await self.join(message.author)

#        if(message.content == self.prefix + "move"):
#            await self.join(message.author, force=True)

        if(message.content == self.prefix + "help" or message.content == self.prefix + "commands"):
            await self.display_help(message.channel)

        if(message.content == self.prefix + "shuffle"):
            await self.shuffle_list(message)

        if(message.content == self.prefix + "c" or message.content == self.prefix + "current"):
            await self.current_song()

        if(message.content == self.prefix + "leave"):
            await self.leave()

        if(message.content == self.prefix + "clear"):
            await self.clear_queue(message)

        if(message.content == self.prefix + "sleep"):
            await self.send_message(message.channel, "Sleeping for five secounds")
            await self.long_task()
            await self.send_message(message.channel, "Finished sleeping!")

        if(message.content.split(' ')[0] == self.prefix + "move" and len(message.content.split(' ')) == 3):
            ind1 = message.content.split(' ')[1]
            ind2 = message.content.split(' ')[2]
            await self.move_song(ind1, ind2)

        if((message.content.split(' ')[0] == self.prefix + "p" or message.content.split(' ')[0] == self.prefix + "play")):
            urls = []

            if(self.voice_client is None):
                await self.join(message.author)

            requested = ' '.join(message.content.split(' ')[1:])

            if("spotify" in requested):
                urls = await spotify_appender(requested)
            elif("soundcloud" in requested and "sets" in requested and not "?in" in requested):
                urls = await soundcloud_set_appender(requested)
            else:
                urls = await general_appender(requested)


            print(urls)
            for url in urls:
                print("URL :", url)
                s = Song(url['url'], url['name'], url['artist'], message.author.display_name, url['duration'])
                self.songs.append(s)

            if(len(urls) > 0):
                await message.add_reaction('\u2705')
            else:
                await message.add_reaction('\u26D4')
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
            embed = discord.Embed(
                title=':fast_forward: **Song Skipped**',
                color=discord.Color.blue()
            )

            await message.channel.send(embed=embed)

        if(message.content == self.prefix + "stop"):
            await self.leave()
            embed = discord.Embed(
                title=':stop_button: **Player Stopped**',
                color=discord.Color.blue()
            )

            await message.channel.send(embed=embed)

        if(message.content == self.prefix + "stats"):
            locally, globally = get_stats(message.guild.id, message.author.id, self.users_path)
            embed = discord.Embed(
                title=f":books: **{message.author.display_name}'s Statistics**",
                color=discord.Color.blue()
            )
            embed.add_field(name=f'Songs Played in this server: {locally}', value="", inline=False)
            embed.add_field(name=f'Songs Played in this anywhere: {globally}', value="", inline=False)

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
                #print(f"I'm connected in channel with other users, use {self.prefix}move to override")
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

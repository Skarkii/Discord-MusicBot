import threading
from tokenize import String
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
        self.last_activity_time = time.time()
        self.disconnect_after_idle_time = float(config['DISCORD']['IDLE_TIMEOUT']) * 60

        self.channel = None #temp

        self.bot.loop.create_task(self.check_idle())

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
        self.last_activity_time = time.time()

    async def start_playing(self, song):
        self.is_playing = True
        try:
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

            playback_url = await song.get_playback_url()
            print("RETRIEVED PLAYBACK URL :", playback_url)

            source = await discord.FFmpegOpusAudio.from_probe(playback_url, **FFMPEG_OPTIONS)
            self.current = song
            self.voice_client.play(source, after=lambda error: self.on_finished_play(song, error))

            embed = discord.Embed(
                title=':headphones: Song Playing Now',
                description= f'[{song.name}]({song.url})',
                color=discord.Color.blue()
            )
            embed.add_field(name=f'**Requester:** {song.requested_by}', value='', inline=False)
            await self.channel.send(embed=embed)
        except Exception as e:
            print(f"Error playing song: {e}")

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
        embed.add_field(name=f'**stats(WIP)** - Displays stats about you', value='', inline=False)
        embed.add_field(name=f'**help** - display this message', value='', inline=False)
        embed.add_field(name=f'**about** - Displays the information about the bot', value='', inline=False)

        await self.channel.send(embed=embed)

    async def get_total_duration(self):
        duration = 0
        for song in self.songs:
            if(isinstance(song.duration, int)):
                duration = duration + song.duration
        return duration

    async def display_queue(self, channel, page=1):
        embed = None

        if(len(self.songs) <= 0):
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Song queue is empty, use {self.prefix}play to play songs',
                color=discord.Color.blue()
            )
        else:
            total_duration = await self.get_total_duration()
            max_pages = (len(self.songs)//10)+1
            if(page < 1):
                page = 1
            elif(page > max_pages):
                page = max_pages
            embed = discord.Embed(
                title=':headphones: Songs in Queue',
                description= f':scroll: Queue length: {str(len(self.songs))} | Page Number: {page}/{max_pages} | :hourglass: Duration: `{int(total_duration // 60)}:{str(int(total_duration % 60)).zfill(2)}`',
                color=discord.Color.blue()
            )

            i = 0
            skipped = 0
            for song in self.songs:
                if(skipped // 10 < page - 1):
                    skipped = skipped + 1
                    continue

                i = i + 1
                if(i > 10):
                    break

                song_duration_sec, song_duration_min = 0, 0

                if(song.duration is not None):
                    song_duration_min = int(song.duration // 60)
                    song_duration_sec = str(int(song.duration % 60)).zfill(2)

                embed.add_field(
                    name=f'',
                    value=f"`{i+skipped}` **-** [{song.name}]({song.url}) - `{song_duration_min}:{song_duration_sec}`",
                    inline=False
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

        print(f'{message.author} said {message.content}')

        if(message.content[0] == self.prefix):
            self.channel = message.channel
        else:
            return

        if(message.content == self.prefix + "join"):
            await self.join(message.author, message)
            await message.add_reaction('\u2705')
            return

        if(message.content == self.prefix + "help" or message.content == self.prefix + "commands"):
            await self.display_help(message.channel)
            return

        if(message.content == self.prefix + "shuffle"):
            await self.shuffle_list(message)
            return

        if(message.content == self.prefix + "c" or message.content == self.prefix + "current"):
            await self.current_song()
            return

        if(message.content == self.prefix + "leave"):
            await message.add_reaction('\u2705')
            await self.leave()
            return

        if(message.content == self.prefix + "clear"):
            await self.clear_queue(message)
            return

        if(message.content == self.prefix + "about"):
            embed = discord.Embed(
                title='Discord MusicBot',
                description= f'Repo: https://github.com/Skarkii/Discord-MusicBot\nVersion: {self.bot.version}',
                color=discord.Color.blue()
            )

            await self.channel.send(embed=embed)
            return


        if(message.content.split(' ')[0] == self.prefix + "move" and len(message.content.split(' ')) == 3):
            ind1 = message.content.split(' ')[1]
            ind2 = message.content.split(' ')[2]
            await self.move_song(ind1, ind2)
            return

        if((message.content.split(' ')[0] == self.prefix + "p" or message.content.split(' ')[0] == self.prefix + "play")):
            urls = []

            if(len(message.content.split(' ')) <= 1):
                embed = discord.Embed(
                    title=':x: **You need to include a link or search query**',
                    description=f'USAGE:\n{self.prefix}p Best song ever\nor\n{self.prefix}p https://www.youtube.com/watch?v=o_v9MY_FMcw',
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
                await message.add_reaction('\u26D4')
                return


            if(self.voice_client is None):
                await self.join(message.author, message)

            requested = ' '.join(message.content.split(' ')[1:])

            if("spotify" in requested):
                if(config['SPOTIFY']['ENABLED'] != "True"):
                    print("Spotify is disabled!")
                    embed = discord.Embed(
                        title=':x: **Spotify is not Enabled**',
                        color=discord.Color.blue()
                    )
                    await message.channel.send(embed=embed)
                    await message.add_reaction('\u26D4')
                    return

                urls = await spotify_appender(requested)
            elif("soundcloud" in requested and "sets" in requested and not "?in" in requested):
                urls = await soundcloud_set_appender(requested)
            else:
                urls = await general_appender(requested)

            songs_added = 0
            for url in urls:
                if((url['name'] == "[Deleted video]" or url['name'] == "[Private video]")):
                    continue
                s = Song(url['url'], url['name'], url['artist'], message.author.display_name, url['duration'])
                self.songs.append(s)
                songs_added = songs_added + 1

            add_song_played("./db.json", message.guild.id, message.author.id, songs_added)
            print(songs_added)


            if(songs_added > 0):
                await message.add_reaction('\u2705')
            else:
                await message.add_reaction('\u26D4')
            return

        if(message.content == self.prefix + "pause"):
            try:
                if(self.is_paused):
                    self.voice_client.resume()
                else:
                    self.voice_client.pause()
            except AttributeError:
                await message.add_reaction('\u26D4')
                embed = discord.Embed(
                    title=':x: **I am not in any channel, I can not pause**',
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
                return

            self.is_paused = not self.is_paused
            await message.add_reaction('\u2705')
            return

        if(message.content.split(' ')[0] == self.prefix + "queue" or message.content.split(' ')[0] == self.prefix + "q"):
            if(len(message.content.split(' ')) > 1):
                if(message.content.split(' ')[1].isnumeric()):
                    page = int(message.content.split(' ')[1])
                    await self.display_queue(message.channel, page)
                    return

            await self.display_queue(message.channel)
            return

        if(message.content == self.prefix + "skip"):
            try:
                self.voice_client.stop()
                embed = discord.Embed(
                    title=':fast_forward: **Song Skipped**',
                    color=discord.Color.blue()
                )

                await message.channel.send(embed=embed)
            except AttributeError:
                embed = discord.Embed(
                    title=':x: **I am not playing any music, I can not skip**',
                    color=discord.Color.blue()
                )

                await message.channel.send(embed=embed)
            return

        if(message.content == self.prefix + "stop"):
            try:
                self.voice_client.stop()
                await self.leave()
                embed = discord.Embed(
                    title=':stop_button: **Player Stopped**',
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)
            except AttributeError:
                embed = discord.Embed(
                    title=':x: **I am not playing**',
                    color=discord.Color.blue()
                )
                await message.channel.send(embed=embed)

            return

        if(message.content == self.prefix + "stats"):
            locally, globally, is_admin, is_banned = get_stats(message.guild.id, message.author.id, "./db.json")
            embed = discord.Embed(
                title=f":books: **{message.author.display_name}'s Statistics**",
                color=discord.Color.blue()
            )
            embed.add_field(name=f'Songs Played in this server: {locally}', value="", inline=False)
            embed.add_field(name=f'Songs Played in this anywhere: {globally}', value="", inline=False)
            embed.add_field(name=f'admin: {is_admin}', value="", inline=False)
            embed.add_field(name=f'banned: {is_banned}', value="", inline=False)

            await message.channel.send(embed=embed)
            return


    async def send_message(self, channel, msg):
        await channel.send(msg)

    async def join(self, author, message, force=False):
        try:
            channel = author.voice.channel
        except:
            embed = discord.Embed(
                title=f"**You need to be in a channel to play music!**",
                color=discord.Color.blue()
            )
            await message.channel.send(embed=embed)
            return


        if(channel == self.current_server):
            print("Already in that server")
            return

        if(self.voice_client is None):
            self.voice_client = await channel.connect(self_deaf=True)
            self.current_server = channel
        else:
            if(len(self.current_server.members) > 1 and force == False):
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

    async def check_idle(self):
        while self.is_running:
            await asyncio.sleep(10)
            if not self.is_playing and time.time() - self.last_activity_time > self.disconnect_after_idle_time:
                print("No one wants to listen to any bangers, I guess I'll leave....")
                embed = discord.Embed(
                    title=":stop_button: **No one wants to listen to any bangers, I guess I'll leave....**",
                    color=discord.Color.blue()
                )
                await self.channel.send(embed=embed)

                await self.leave()
                break

    async def on_kicked(self):
        await self.leave()

    async def on_move(self, new_channel):
        self.current_server = new_channel

        await self.voice_client.move_to(new_channel)

        if(not self.is_paused):
            await asyncio.sleep(0.5)
            self.voice_client.resume()

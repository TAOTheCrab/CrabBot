#!/usr/bin/env python3
# CrabBot general voice commands, for Discord v1.0
#
# Reference:
# https://github.com/Rapptz/discord.py/blob/rewrite/examples/basic_voice.py

import asyncio
import logging  # I want to keep track of command usage and voice state for troubleshooting
from pathlib import Path
import random

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext.commands import Cog, command, CommandError
import youtube_dl

from crabbot.common import read_list_file


""" This block mostly taken straight from discord.py's examples/basic_voice.py """
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
""" End discord.py examples/basic_voice.py copied code block """


class Voice(Cog):
    def __init__(self, bot_loop, memes_path, use_libav=False):
        self.bot_loop = bot_loop
        self.decoder_executable = 'ffmpeg' if use_libav is False else 'avconv'

        self.memes_path = Path(memes_path)
        # Initialize lists
        self.update_lists()

        self.voice_client = None  # For handling state of the player. Possibly unwise.

    def update_lists(self):
        # !memes
        self.the_memes = read_list_file(self.memes_path / "filelist.txt")

    def disconnect_after_playback(self, error):
        # NOTE ESSENTIALLY NOT IMPLEMENTED YET
        if error:
            logging.info(f"Error with voice: {error}")
        #TODO Figure out if it's possible to disconnect when playback is exausted without await
        # OLD CODE: asyncio.ensure_future(self.voice_client.disconnect, loop=self.bot_loop)
        

    @command(help="Lost?")
    async def memes(self, ctx):
        logging.info("Playing voice memes")

        chosen_meme = random.choice(self.the_memes)

        source = FFmpegPCMAudio(str(self.memes_path / chosen_meme))
        ctx.voice_client.play(source, after=None)  # NOTE removing `after=disconnect_after_playback` until that works correctly
        # BUG possibly in discord.py? in player.py/cleanup(), it tries to kill ffmpeg, which appears to have terminated on its own (EOF?)
        #     cleanup() never gets past attempting to kill its subprocess, never performs `after`. (NOTE only tested on WSL Ubuntu)
        #     commenting out line 180's `proc.kill()` seems to have no ill effects in this particular use case, and discord.py thinks it's terminated.
        self.voice_client = ctx.voice_client  # Possibly ill-fated attempt to disconnect after playback is exausted.

        # Now voice_client.play() will go on its own, command ends

    @command(help="Stream anything YouTube-DL supports (no queue yet)")
    async def stream(self, ctx, *, url):
        """ Taken from discord.py's examples/basic_voice.py """

        # TODO queue by reference counting and then decrementing with after?

        logging.info(f'Streaming "{url}" from "{ctx.message.channel}" on "{ctx.message.guild}"')

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot_loop, stream=True) # NOTE If voice has problems, try setting stream=False first
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        logging.info(f'Stream setup successfull. Now playing "{player.title}" in "{ctx.author.voice.channel.name}"')
        await ctx.send(f'Now playing: {player.title}')

    @memes.before_invoke
    @stream.before_invoke
    async def ensure_voice_with_interrupt(self, ctx):
        """ Taken from discord.py's examples/basic_voice.py 
        
        Will interrupt the currently playing audio in favor of the next command.
        """
        if ctx.voice_client is None:
            if ctx.author.voice is not None:
                await ctx.author.voice.channel.connect()
                logging.info(f'Connected to "{ctx.author.voice.channel.name}" on server "{ctx.guild.name}"')
            else:
                await ctx.send(f"{ctx.author.mention} You must be in a voice channel to use voice commands")
                logging.info("Author is not connected to a voice channel, voice command stopped.")
                raise CommandError("Author is not connected to a voice channel")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    @command(help="Disconnect from voice", aliases=["shutup"])
    async def disconnect(self, ctx):
        if ctx.voice_client is not None:
            logging.info(f'Ending voice connection to "{ctx.voice_client.channel.name}" on server "{ctx.voice_client.guild}"')

            await ctx.voice_client.disconnect()
        else:
            # We could just not do anything, but I like when there's feedback, debugging or not
            await ctx.send(f"The bot is not currently connected to a voice channel in {ctx.message.guild}")

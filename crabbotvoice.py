#!/usr/bin/env python3

import crabbot  # needed for read_list_file to create the_memes

import discord
from discord.ext import commands
import logging
from pathlib import Path
import random


class Voice:
    def __init__(self, bot, use_libav=False):
        # TODO make configurable
        self.memes_path = Path("assets/memes")
        # Initialize list
        self.update_voice_list()

        self.bot = bot
        self.use_libav = use_libav

        # NOTE code should be reworked to remove these, using checks for exists instead of None
        self.voice_connection = None
        self.voice_player = None

        self.voice_volume = 0.2
        self.max_volume = 1.0

    def update_voice_list(self):
        # !memes
        # TODO? instead, iterate over or choose from the contents of memes_path
        self.the_memes = crabbot.read_list_file(self.memes_path / "filelist.txt")

    async def connect_voice(self, ctx):

        logging.info("Attempting a voice connection")

        user_channel = ctx.message.author.voice_channel
        if user_channel is None:
            logging.info("Voice connection aborted: User not in a channel")
            await self.bot.reply("Try being in a voice channel first")
            return

        # Needed for voice playback
        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus')

        try:
            self.voice_connection = await self.bot.join_voice_channel(user_channel)
            logging.info("Voice connected to " + user_channel.name)
        except discord.ClientException as e:
            logging.info(e)

    @commands.command(help="Set the voice volume. 0.0 - 1.0")
    async def volume(self, new_volume):
        self.voice_volume = min(float(new_volume), self.max_volume)

        if self.voice_player is not None:
            self.voice_player.volume = self.voice_volume

    @commands.command()
    async def maxvolume(self, new_volume):
        self.max_volume = min(float(new_volume), 1.0)

    @commands.command(aliases=['voice_stop', 'shutup'])
    async def stop_voice(self):
        logging.info("Attempting to stop voice")

        if self.voice_player is not None:
            self.voice_player.stop()
            logging.info("Voice player stopped")

        # Even if there is no connection, disconnect() should simply do nothing
        logging.info("Disconnecting from voice")
        await self.voice_connection.disconnect()
        logging.info("Voice disconnected")

    def end_playback(self):
        # NOTE put any playback queue checks here

        logging.info("Ending voice playback")
        disconnect_function = self.voice_connection.disconnect()
        # BUG seems to get stuck here. Related to Python docs section 18.5.9.6?
        self.bot.loop.call_soon_threadsafe(disconnect_function)
        logging.info("Voice playback ended")

    @commands.command(pass_context=True, help="Lost?")
    async def memes(self, ctx):
        await self.connect_voice(ctx)

        self.voice_player = self.voice_connection.create_ffmpeg_player(
            str(self.memes_path) + '/' + random.choice(self.the_memes),
            use_avconv=use_libav,
            after=self.end_playback)
        self.voice_player.volume = self.voice_volume

        self.voice_player.start()

        logging.info("Started memes")

    @commands.command(pass_context=True,
                      help="Plays most things supported by youtube-dl")
    async def stream(self, ctx, video=None):
        if video is not None:
            await self.connect_voice(ctx)

            # TODO further testing. end_playback doesn't seem to trigger
            #      (might be computer-specific)
            #      Might be silent ignore of RuntimeException for async not being awaited
            self.voice_player = await self.voice_connection.create_ytdl_player(
                video,
                use_avconv=use_libav,
                after=self.end_playback)
            self.voice_player.volume = self.voice_volume

            self.voice_player.start()

            logging.info("Started streaming " + self.voice_player.title)

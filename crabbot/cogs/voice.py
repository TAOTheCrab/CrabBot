#!/usr/bin/env python3
# CrabBot general voice commands
#
# Parts taken from discord.py/examples/playlist.py
# https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

import asyncio
import importlib.util
import logging
from pathlib import Path
import random
import tempfile

import discord
from discord.ext import commands

import crabbot.common


class Voice:
    def __init__(self, bot, memes_path, use_libav=False):
        self.bot = bot
        self.use_libav = use_libav

        self.memes_path = Path(memes_path)
        # Initialize lists
        self.update_lists()

        # dict: server->voice_connection
        self.voice_connections = {}

    # Special function used by discord.py for remove_cog
    def __unload(self):
        # Cancel all audio tasks and disconnect
        for server, connection in self.voice_connections.items():
            logging.info("Cancelling connection to {}".format(server))
            try:
                connection.audio_player.cancel()
                if connection.voice is not None:
                    # can take a long time if cog is removed while playing. Is there a fix?
                    self.bot.loop.create_task(connection.voice.disconnect())
            except:
                pass

    def update_lists(self):
        # !memes
        self.the_memes = crabbot.common.read_list_file(self.memes_path / "filelist.txt")

    def remove_voice_connection(self, server):
        logging.info("Removing connection to voice {}".format(server))
        del self.voice_connections[server]

    def get_voice_connection(self, ctx):
        """Either retrieves or creates a voice connection entry for the server of the given ctx"""
        logging.info("Getting a voice connection")

        # Needed for voice playback. Deferred until we start possibly needing it
        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus')

        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Using existing voice connection")
            return existing_connection
        else:
            new_connection = VoiceConnection(self.bot)
            self.voice_connections[ctx.message.server] = new_connection
            logging.info("New voice connection to {} added".format(ctx.message.server))
            return new_connection

    async def setup_voice_connection(self, ctx):
        target_voice_channel = ctx.message.author.voice_channel

        if target_voice_channel is None:
            logging.info("User not in a voice channel")
            self.bot.loop.create_task(self.bot.reply("You must be in a voice channel to use voice commands"))
            return None, None

        voice_connection = self.get_voice_connection(ctx)

        # Initialize voice if not already created
        if voice_connection.voice is None:
            # BUG if two users use a command ~simultaneously, this gets called twice (voice still None) and crashes
            logging.info("Initializing voice from a command")
            await voice_connection.connect(target_voice_channel)
            target_voice_channel = None

        return target_voice_channel, voice_connection  # Caller generally needs both

    @commands.command(pass_context=True)
    async def volume(self, ctx, new_volume=None):
        voice_connection = self.get_voice_connection(ctx)
        if new_volume is None:
            await self.bot.say("The current volume is {}".format(voice_connection.volume))
            return

        logging.info("Setting volume for {} to {}".format(ctx.message.server, new_volume))
        # Barring Exceptions, we should always get back something we can set_volume for
        voice_connection.set_volume(new_volume)

    @commands.command(pass_context=True)
    async def maxvolume(self, ctx, new_volume=None):
        voice_connection = self.get_voice_connection(ctx)
        if new_volume is None:
            await self.bot.say("The current max volume is {}".format(voice_connection.maxvolume))
            return

        logging.info("Setting max volume for {} to {}".format(ctx.message.server, new_volume))
        # Barring Exceptions, we should always get back something we can set_maxvolume for
        voice_connection.set_maxvolume(new_volume)

    @commands.command(aliases=['voice_stop', 'shutup'], pass_context=True,
                      help="Stop all playback and empty the play queue")
    async def stop_voice(self, ctx):
        logging.info("Ending voice connection to {}".format(ctx.message.server))
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Stopping the voice player")

            if existing_connection.current_entry.player is not None:
                # Stop the current audio ASAP
                existing_connection.current_entry.player.stop()

            # Empty the queue and get the audio player task to cleanup itself
            existing_connection.empty_queue()
            existing_connection.toggle_next()

            # Audio player task should do this cleanup for us, but just in case (ex. crash?)
            if existing_connection.voice is not None:
                # BUG? Somehow the Connection loop can set voice to None, log a dc, but not disconnect
                logging.info("Disconnecting voice")
                await existing_connection.voice.disconnect()
                logging.info("Voice connection ended")
                existing_connection.voice = None

            logging.info("Voice stopped")

        else:
            logging.info("No voice connection to end")
            await self.bot.say("No voice connection to {}".format(ctx.message.server))

    @commands.command(pass_context=True,
                      help="Skip the currently playing audio for the next queued entry")
    async def skip(self, ctx):
        logging.info("Stopping current audio entry for {}".format(ctx.message.server))
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Stopping the voice player")
            if existing_connection.current_entry.player is not None:
                existing_connection.current_entry.player.stop()
            # Audio player task should now continue

    @commands.command(pass_context=True, help="Lost?")
    async def memes(self, ctx):
        logging.info("Memeing it up")

        chosen_meme = random.choice(self.the_memes)

        target_voice_channel, voice_connection = await self.setup_voice_connection(ctx)

        if voice_connection is None:
            logging.info("Aborting memes")
            return

        # Build a VoiceEntry
        player = voice_connection.voice.create_ffmpeg_player(
            str(self.memes_path) + '/' + chosen_meme,
            use_avconv=self.use_libav,
            after=voice_connection.toggle_next)
        new_entry = VoiceEntry(player, chosen_meme, target_voice_channel)

        logging.info("Queueing new voice entry for {}".format(new_entry.name))
        voice_connection.prepare_player()
        await voice_connection.audio_queue.put(new_entry)

    @commands.command(pass_context=True,
                      help="Plays most things supported by youtube-dl\n"
                           "Accepts a start time in the format [HH:MM]:SS (feature may be buggy)")
    async def stream(self, ctx, video=None, start_time='00:00:00'):
        # TODO check if video is a valid streamable (YoutubeDL.py simulate?)
        if video is None:
            self.bot.reply("Nothing to stream")
            return

        logging.info("Streaming")

        if importlib.util.find_spec("youtube_dl") is None:
            # Preempt import error and silent failure with a more useful message and user feedback
            logging.error("Memes command requires youtube-dl module. Install with pip.")
            self.bot.reply("Bot is not configured to stream")
            return

        target_voice_channel, voice_connection = await self.setup_voice_connection(ctx)

        if voice_connection is None:
            logging.info("Aborting streaming")
            return

        # Build a VoiceEntry
        # See YoutubeDL.py for ytdl options:
        # https://github.com/rg3/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L128
        ytdl_opts = {
            # "ignoreerrors": True  # Mostly so it won't stop on bad playlist entries
            "noplaylist": True  # Too many things broke on playlists, so...
        }
        ffmpeg_before_options="-ss " + start_time
        player = await voice_connection.voice.create_ytdl_player(
            video,
            use_avconv=self.use_libav,
            ytdl_options=ytdl_opts,
            before_options=ffmpeg_before_options,
            after=voice_connection.toggle_next)
        new_entry = VoiceEntry(
            player, player.title,
            target_voice_channel, ctx.message)

        # Give user feedback when recieved
        await self.bot.reply("Stream queued")

        logging.info("Queueing new voice entry for {}".format(new_entry.name))
        voice_connection.prepare_player()
        await voice_connection.audio_queue.put(new_entry)


class VoiceEntry:
    def __init__(self, player, name, voice_channel, message=None):
        self.player = player
        self.name = name
        self.voice_channel = voice_channel
        if message is not None:
            self.requester = message.author
            self.text_channel = message.channel
        else:
            self.requester = None
            self.text_channel = None


class VoiceConnection:
    def __init__(self, bot):
        self.bot = bot

        self.voice = None
        self.current_entry = None
        self.play_next_in_queue = asyncio.Event()
        self.audio_queue = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self.maxvolume = 1.0
        self.volume = 0.2

    def set_volume(self, new_volume):
        self.volume = min(float(new_volume), self.maxvolume)
        if self.current_entry is not None:
            self.current_entry.player.volume = self.volume

    def set_maxvolume(self, new_volume):
        # Max volume hardcoded to 100%
        self.maxvolume = min(float(new_volume), 1.0)

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_in_queue.set)

    async def connect(self, channel):
        if self.voice is None:
            logging.info("Attempting voice connection to {}".format(channel.name))
            try:
                self.voice = await self.bot.join_voice_channel(channel)
                logging.info("Voice connected to {}".format(channel.name))
            except discord.ClientException as e:
                logging.info(e)
                await self.bot.say("Sorry, something went wrong with voice")
        else:
            logging.info("Moving existing voice connection to {}".format(channel.name))
            await self.voice.move_to(channel)

    def prepare_player(self):
        ''' Ensure audio player is in a usable state '''
        # This mostly involves restarting the task if it's done
        if self.audio_player.done():
            self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def empty_queue(self):
        # Remake the queue as a way of emptying it
        self.audio_queue = asyncio.Queue()

    async def audio_player_task(self):
        while True:  # We want to wait for at least one entry, so can't check empty() here
            self.play_next_in_queue.clear()

            # Wait for a VoiceEntry
            logging.info("Audio player task ready. Waiting for next VoiceEntry")
            self.current_entry = await self.audio_queue.get()
            logging.info("VoiceEntry recieved")

            # Connect to a voice channel. None means the command did it already.
            if self.current_entry.voice_channel is not None:
                await self.connect(self.current_entry.voice_channel)

            logging.info("Playing {} on {}".format(
                self.current_entry.name, self.voice.channel))
            # Log the duration (eg. for ytdl_player)
            # if hasattr(self.current_entry.player, 'duration'):
            #    # BUG TypeError: unsupported operand type(s) for divmod(): 'NoneType' and 'int'
            #    #   Guess ytdl_player always has duration, just not always with an answer
            #    #   ex. for raw mp3 files. Disabling for now.
            #    logging.info("Player length is {0[0]}m {0[1]}s".format(
            #        divmod(self.current_entry.player.duration, 60)))
            if self.current_entry.requester is not None:
                # Notify the requester at the text channel the request was sent from
                logging.info("Requested by {}".format(self.current_entry.requester))
                msg = "{0.mention}, Playing your stream: {1}".format(
                    self.current_entry.requester, self.current_entry.name)
                await self.bot.send_message(self.current_entry.text_channel, msg)

            self.current_entry.player.volume = self.volume
            self.current_entry.player.start()

            # Wait for playback to finish (player.after = *connection_instance*.toggle_next())
            await self.play_next_in_queue.wait()
            logging.info("Audio finished")

            # Small pause between entries
            asyncio.sleep(1)

            if self.audio_queue.empty():
                break

            # End of loop

        logging.info("Audio queue finished")
        # The disconnect sound doesn't make a good sudden end
        asyncio.sleep(1)

        # BUG there's a small window where you can call a command while it's disconnecting
        #  So the command goes through, but the VoiceEntry disappears

        voice_channel_name = self.voice.channel
        logging.info("Disconnecting from voice channel {}".format(voice_channel_name))
        await self.voice.disconnect()
        logging.info("Voice has been disconnected for channel {}".format(voice_channel_name))
        self.voice = None

        # End of task, be sure to restart task if it is needed again

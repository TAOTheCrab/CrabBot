#!/usr/bin/env python3
# Parts taken from discord.py/examples/playlist.py
# https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

import asyncio
import logging
from pathlib import Path
import random

import discord
from discord.ext import commands

import crabbot.common


class Voice(crabbot.common.CrabBotCog):
    has_lists = True

    def __init__(self, bot, use_libav=False):
        super().__init__(bot)
        self.use_libav = use_libav

        # TODO make configurable
        self.memes_path = Path("assets/memes")
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
                    # BUG can take a long time if cog is removed while playing
                    self.bot.loop.create_task(connection.voice.disconnect())
            except:
                pass

    def update_lists(self):
        # !memes
        self.the_memes = crabbot.common.read_list_file(self.memes_path / "filelist.txt")

    def remove_voice_connection(self, server):
        logging.info("Removing connection to voice {}".format(server))
        del self.voice_connections[server]

    def create_voice_connection(self, ctx):
        logging.info("Creating a voice connection")

        user_voice_channel = ctx.message.author.voice_channel
        if user_voice_channel is None:
            logging.info("Voice connection not created: User not in a channel")
            self.bot.loop.create_task(self.bot.reply("Try being in a voice channel first"))
            return None

        # Needed for voice playback. Deferred until we start possibly needing it
        if not discord.opus.is_loaded():
            discord.opus.load_opus('opus')

        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Using existing voice connection")
            return existing_connection

        else:
            new_connection = VoiceConnection(
                self.bot,
                after=self.remove_voice_connection)
            self.voice_connections[ctx.message.server] = new_connection
            logging.info("New voice connection to {} added".format(ctx.message.server))
            return new_connection

    @commands.command(pass_context=True)
    async def volume(self, ctx, new_volume):
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            existing_connection.set_volume(new_volume)
        else:
            await self.bot.say("No voice connection to set a volume for")
            # TODO think about persistent volume settings

    @commands.command(pass_context=True)
    async def maxvolume(self, ctx, new_volume):
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            existing_connection.set_maxvolume(new_volume)
        else:
            await self.bot.say("No voice connection to set a volume for")
            # TODO think about persistent volume settings

    @commands.command(aliases=['voice_stop', 'shutup'], pass_context=True)
    async def stop_voice(self, ctx):
        logging.info("Ending voice connection to {}".format(ctx.message.server))
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Stopping the voice player")
            # TODO check current_player "is not None"
            #   It shouldn't be None too often, but eg. stream's delay might cause an edge case
            # Stop the current audio ASAP
            existing_connection.current_entry.player.stop()

            # Since we can't be sure there isn't more audio queued, force stop the task
            existing_connection.audio_player.cancel()
            logging.info("Disconnecting voice")
            await existing_connection.voice.disconnect()
            logging.info("Voice connection ended")

            self.remove_voice_connection(ctx.message.server)
        else:
            logging.info("No voice connection to end")
            await self.bot.say("No voice connection to {}".format(ctx.message.server))
        # TODO think about persistent volume settings

    @commands.command(aliases=['current_stop', 'skip'], pass_context=True)
    async def stop_current(self, ctx):
        logging.info("Stopping current audio entry for {}".format(ctx.message.server))
        existing_connection = self.voice_connections.get(ctx.message.server)
        if existing_connection is not None:
            logging.info("Stopping the voice player")
            # TODO check current_player "is not None"
            existing_connection.current_entry.player.stop()
            # Audio player task should now continue

    @commands.command(pass_context=True, help="Lost?")
    async def memes(self, ctx):
        logging.info("Memeing it up")

        voice_connection = self.create_voice_connection(ctx)
        # If the user was not found to be in a voice channel, end the command
        if voice_connection is None:
            return

        chosen_meme = random.choice(self.the_memes)

        target_voice_channel = ctx.message.author.voice_channel
        # Initialize voice if not already created
        if voice_connection.voice is None:
            await voice_connection.connect(target_voice_channel)
            target_voice_channel = None

        # Build a VoiceEntry
        player = voice_connection.voice.create_ffmpeg_player(
            str(self.memes_path) + '/' + chosen_meme,
            use_avconv=self.use_libav,
            after=voice_connection.toggle_next)
        new_entry = VoiceEntry(player, chosen_meme, target_voice_channel)

        logging.info("Queueing new voice entry for {}".format(new_entry.name))
        await voice_connection.audio_queue.put(new_entry)

    @commands.command(pass_context=True,
                      help="Plays most things supported by youtube-dl")
    async def stream(self, ctx, video=None):
        if video is None:
            # TODO check if video is a valid streamable (YoutubeDL.py simulate?)
            self.bot.reply("Nothing to stream")
            return

        logging.info("Streaming")

        voice_connection = self.create_voice_connection(ctx)
        # If the user was not found to be in a voice channel, end the command
        if voice_connection is None:
            return

        # Give user feedback when recieved
        await self.bot.reply("Stream queued")

        target_voice_channel = ctx.message.author.voice_channel
        # Initialize voice if not already created
        if voice_connection.voice is None:
            await voice_connection.connect(target_voice_channel)
            target_voice_channel = None

        # Build a VoiceEntry
        player = await voice_connection.voice.create_ytdl_player(
            video,
            use_avconv=self.use_libav,
            after=voice_connection.toggle_next)
        new_entry = VoiceEntry(
            player, player.title,
            target_voice_channel, ctx.message)

        logging.info("Queueing new voice entry for {}".format(new_entry.name))
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
    def __init__(self, bot, after):
        self.bot = bot
        self.after = after

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

    async def audio_player_task(self):
        # Play audio until the queue is empty, then disconnect
        # We're assuming at least one entry comes in per VoiceConnection
        # which seems to be a problem mostly with ytdl and its processing time
        queue_has_entries = True
        while queue_has_entries:
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
            if hasattr(self.current_entry.player, 'duration'):
                logging.info("Player length is {0[0]}m {0[1]}s".format(
                    divmod(self.current_entry.player.duration, 60)))
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
            queue_has_entries = not self.audio_queue.empty()

        logging.info("Audio queue finished")
        # The disconnect sound doesn't make a good sudden end
        asyncio.sleep(1)

        logging.info("Disconnecting from voice channel {}".format(self.voice.channel))
        # BUG there's a small window where you can call a command while it's disconnecting
        #  So the command goes through, but the VoiceEntry disappears
        await self.voice.disconnect()
        # TODO maybe instead just set voice to None for ex. volume persistence per server
        #      Currently the VoiceConnection has to remove itself to reset the task
        self.after(self.voice.server)

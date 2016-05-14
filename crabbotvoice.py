#!/usr/bin/env python3

import crabbot

import discord
import logging
from pathlib import Path
import random


memes_path = Path("assets/memes")

# NOTE code should be reworked to remove these, using checks for exists instead of None
voice_connection = None
voice_player = None

voice_volume = 0.2
max_volume = 1.0


def update_voice_list():
    # !memes
    # TODO? instead, iterate over or choose from the contents of memes_path
    global the_memes
    the_memes = crabbot.read_list_file(memes_path / "filelist.txt")

# Initialize list
update_voice_list()


async def connect_voice(ctx):
    # Might be nice to check if voice is True, but for now
    # disabling commands should be enough

    logging.info("Attempting a voice connection")

    user_channel = ctx.message.author.voice_channel
    if user_channel is None:
        logging.info("Voice connection aborted: User not in a channel")
        await crabbot.bot.reply("Try being in a voice channel first")
        return

    # Needed for voice playback
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

    global voice_connection

    try:
        voice_connection = await crabbot.bot.join_voice_channel(user_channel)
        logging.info("Voice connected to " + user_channel.name)
    except discord.ClientException as e:
        logging.info(e)


@crabbot.crabcommand(help="Set the voice volume. 0.0 - 1.0")
async def volume(new_volume):
    global voice_volume
    voice_volume = min(float(new_volume), max_volume)

    if voice_player is not None:
        voice_player.volume = voice_volume


@crabbot.crabcommand()
async def maxvolume(new_volume):
    global max_volume
    max_volume = min(float(new_volume), 1.0)


@crabbot.crabcommand(aliases=['voice_stop', 'shutup'])
async def stop_voice():
    global voice_player  # just to be explicit. Might want to set player to None later?

    logging.info("Attempting to stop voice")

    if voice_player is not None:
        voice_player.stop()
        logging.info("Voice player stopped")

    # Even if there is no connection, disconnect() should simply do nothing
    logging.info("Disconnecting from voice")
    await voice_connection.disconnect()
    logging.info("Voice disconnected")


def end_playback():
    # NOTE put any playback queue checks here

    logging.info("Ending voice playback")
    disconnect_function = voice_connection.disconnect()
    crabbot.bot.loop.call_soon_threadsafe(disconnect_function)
    logging.info("Voice playback ended")


@crabbot.crabcommand(pass_context=True, help="Lost?")
async def memes(ctx):
    await connect_voice(ctx)

    global voice_player  # in meantime global player var?
    voice_player = voice_connection.create_ffmpeg_player(
        str(memes_path) + '/' + random.choice(the_memes),
        after=end_playback)
    voice_player.volume = voice_volume

    voice_player.start()

    logging.info("Started memes")


@crabbot.crabcommand(pass_context=True,
                     help="Plays most things supported by youtube-dl")
async def stream(ctx, video=None):
    if video is not None:
        await connect_voice(ctx)

        # TODO further testing. end_playback doesn't seem to trigger
        #      (might be computer-specific)
        #      Might be silent ignore of RuntimeException for async not being awaited
        global voice_player
        voice_player = await voice_connection.create_ytdl_player(
            video,
            after=end_playback)
        voice_player.volume = voice_volume

        voice_player.start()

        logging.info("Started streaming " + voice_player.title)

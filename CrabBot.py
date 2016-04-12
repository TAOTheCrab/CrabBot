#!/usr/bin/env python3
# NOTE: using Python3.5+ async syntax
# Simple Discord chatbot for fun
#
# Requires user.cfg with valid username/password combo

import discord
from discord.ext import commands
import random
import logging
import time

# Needed for voice
# TODO Make optional in some way
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')

bot = commands.Bot(command_prefix='!crab', description="Huh, another bot")

# TODO It would probably be nicer to store these somewhere else
mobas = ["Smite", "SMNC", "Strife", "Overwatch", "HoN", "AoS", "HotS"]
places = ["Desert Bus", "the woods", "a Discord server", "DotA", "a video game",
            "a hall of Ricks", "an interdimensional peace zone", "the TARDIS",
            "Twitch chat", "Dark Souls", "Stack Overflow"]

logging.basicConfig(level=logging.INFO)

# https://github.com/Rapptz/discord.py/blob/async/examples/basic_bot.py
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(hidden=True)
async def update_profile():
    # As far as I can tell, Discord's official API only supports JPEG
    picture = open('CrabBot.jpg', 'rb')
    picture_bits = picture.read()
    picture.close()
    await bot.edit_profile(avatar=picture_bits)
    print("Updated profile")

@bot.command(help='The bots have something to say')
async def takeover():
    await bot.say("Something something robots")

@bot.command(help='Well, what is this Lords Management then?', aliases=['lol'])
async def dota():
    num = random.randint(1, (len(mobas) - 1))
    await bot.say("This is a strange {} mod".format(mobas[num]))

@bot.command(enabled=False, hidden=True)
async def annoy():
    # TODO anti-spam cooldown (probably a good idea for most commands)
    # NOTE so far untested with bot.say version, unsure if tts works
    await bot.say("Ho ho ha ha!", tts=True)

@bot.command(help='For the unruly patron')
async def sir():
    # Yes, possibly having repeats is intentional, more fun that way
    place_one = random.randint(1, (len(places) - 1))
    place_two = random.randint(1, (len(places) - 1))
    reply = "Sir, this is {}, not {}.".format(places[place_one], places[place_two])
    await bot.say(reply)

@bot.command()
async def assist():
    await bot.say("Help is transient, and for some reason is not provided here.")

@bot.command(help="👍")
async def thumbsup(num = '1'):
    if num not in ('nope', '0'):
        try:
            number = int(num)
        except ValueError:
            number = 1
        await bot.reply("👍" * number)
    else:
        await bot.say("Awww")

# https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

async def connect_voice(ctx):
    if bot.is_voice_connected():
        # for now, assume we don't need to reconnect (obv we'll dc at end of function, but for now...)
        # this is mostly just to remind myself that this might be a concern later
        pass
    else:
        channel_name = ctx.message.author.voice_channel
        if channel_name == None:
            await bot.reply("Try being in a voice channel first")
            return

        await bot.join_voice_channel(channel_name)

player = None

# Connects to message author's voice channel, plays music, then disconnects (like Airhorn Solutions)
@bot.command(pass_context=True, help="Lost?")
async def test_voice(ctx):
    await connect_voice(ctx)

    # TODO figure out discord.py cogs (ext/commands/bot.py) for eg. player.stop()
    # in meantime global player var?
    player = bot.voice.create_ffmpeg_player("wayShort.ogg", options='-af "volume=0.2"')
    # TODO figure out if there's an async way to play stuff
    # Examples say this should be player.start(), but that doesn't seem to exist?
    player.run()

    print("stopped playing music")

    if bot.is_voice_connected():
        await bot.voice.disconnect()

@bot.command(pass_context=True)
async def test_yt(ctx, video=None):
    await connect_voice(ctx)

    if video is not None:
        player = await bot.voice.create_ytdl_player(video, options='-af "volume=0.2"')
        player.run()

        print("stopped streaming")

    if bot.is_voice_connected():
        await bot.voice.disconnect()

@bot.command()
async def stop():
    # NOTE: Currently does not work as intended, will not interrupt playback
    # Also tends to just crash by having multiple tasks call disconnect
    # Clearly I do not understand asyncio

    if player is not None:
        # Try to get the player to stop. May not be the right function and/or procedure.
        player.stop()
        print("stopped player")

    if bot.is_voice_connected():
        await bot.voice.disconnect()

# IMPROVEMENT give option to use args instead of cfg file
# if __name__ == "__main__":

# Might want to add more cfg options later
user_cfg = open("user.cfg", 'r')
login = user_cfg.readline().rstrip()
user_cfg.close()

bot.run(login)

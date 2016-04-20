#!/usr/bin/env python3
# NOTE: using Python3.5+ async syntax
# Simple Discord chatbot for fun
#
# Requires a bot user token. See -h for details.

import argparse
import asyncio
import discord
from discord.ext import commands
import logging
import random

# Running the bot

# Do argparse first so that -h can print and exit before anything else happens
parser = argparse.ArgumentParser(description='A silly Discord bot')
token_args = parser.add_mutually_exclusive_group(required=True)
token_args.add_argument('-t', '--token', help="The bot user's login token")
token_args.add_argument('-f', '--file', type=argparse.FileType('r'), help="A file with the bot user's login token as the first line")

# IMPROVEMENT convert update_profile() to optional startup args (safer)
# IMPROVEMENT user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location

args = parser.parse_args()

if args.file is not None:
    login = args.file.readline().rstrip()
    args.file.close()
else:
    login = args.token

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!crab'), description="Huh, another bot")

# End running the bot (more at end of file)

# Begin core bot stuff

# TODO It would probably be nicer to store these somewhere else
# !dota
mobas = ["Smite", "SMNC", "Strife", "Overwatch", "HoN", "AoS", "HotS"]
# !sir
places = ["Desert Bus", "the woods", "a Discord server", "DotA", "a video game",
            "a hall of Ricks", "an interdimensional peace zone", "the TARDIS",
            "Twitch chat", "Dark Souls", "Stack Overflow"]
# !adventure
deaths = ["skewered", "slapped to death", "tickled to sleep", "drowned", "stabbed", "lead pipe'd"]
killers = ["a goblin", "fish", "a knight", "a roving band of thieves", "aliens", "a robot", "Colonel Catsup"]
locations = ["Lordran", "a fish bowl", "space", "the castle", "the living room", "the first dungeon", "the boss room"]
rewards = ["the Amulet of Yendor", "pride", "the Orb of Zot", "... uh, the devs will think of something", "the lordvessel", "humanity"]

logging.basicConfig(level=logging.INFO)

def log_command(used):
    # TODO convert to Context.command. Set pass_context=True for all commands,
    # or look into overriding process_commands
    logging.info("Command: " + used)

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
    picture = open('assets/CrabBot.jpg', 'rb')
    picture_bits = picture.read()
    picture.close()
    await bot.edit_profile(avatar=picture_bits)
    print("Updated profile")

@bot.command(help='The bots have something to say')
async def takeover():
    await bot.say("Something something robots")

@bot.command(help='Well, what is this Lords Management then?', aliases=['lol'])
async def dota():
    moba = random.choice(mobas)
    await bot.say("This is a strange {} mod".format(moba))

@bot.command(enabled=False, hidden=True)
async def annoy():
    # TODO anti-spam cooldown (probably a good idea for most commands)
    # NOTE so far untested with bot.say version, unsure if tts works
    await bot.say("Ho ho ha ha!", tts=True)

@bot.command(help='For the unruly patron')
async def sir():
    log_command("sir")
    # Yes, possibly having repeats is intentional, more fun that way
    place_one = random.choice(places)
    place_two = random.choice(places)
    reply = "Sir, this is {}, not {}.".format(place_one, place_two)
    await bot.say(reply)

@bot.command()
async def assist():
    if random.randint(1, 10) == 5: # 10%
        await bot.say("Ok")
    else:
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

@bot.command(help="Go on a quest!")
async def adventure():
    await bot.say("Simulating adventure...")
    await bot.type()
    await asyncio.sleep(3) # suspense!
    if random.randint(1,10) == 5: # 10% chance to win
        reward = random.choice(rewards)
        await bot.say("You win! You got {}!".format(reward))
    else: # Ruin!
        death = random.choice(deaths)
        killer = random.choice(killers)
        location = random.choice(locations)
        await bot.say("You were {} by {} in {}".format(death, killer, location))

# Begin voice section (pending separation)

# https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

async def connect_voice(ctx):
    # Needed for voice
    # TODO Make optional in some way
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

    channel_name = ctx.message.author.voice_channel
    if channel_name == None:
        await bot.reply("Try being in a voice channel first")
        return None

    try:
        await bot.join_voice_channel(channel_name)
    except discord.ClientException as e:
        await bot.say(e.message)

player = None

@bot.command()
async def stop():

    # TODO figure out global player (currently this is always None). voice.disconnect() covers us, but...
    if player is not None:
        player.stop()
        print("stopped player")

    if bot.is_voice_connected():
        await bot.voice.disconnect()

# TODO? volume control (eg. '-af "volume={}"'.format{x}) be sure to clamp

# Connects to message author's voice channel, plays music, then disconnects (like Airhorn Solutions)
@bot.command(pass_context=True, help="Lost?")
async def test_voice(ctx):
    await connect_voice(ctx)

    # TODO figure out discord.py cogs (ext/commands/bot.py) for ex. player.stop()
    # in meantime global player var?
    player = bot.voice.create_ffmpeg_player("assets/memes/wayShort.ogg", options='-af "volume=0.2"', after=stop)
    player.start()

    logging.info("Started testing voice")

@bot.command(pass_context=True)
async def test_yt(ctx, video=None):
    await connect_voice(ctx)

    if video is not None:
        #
        player = await bot.voice.create_ytdl_player(video, options='-af "volume=0.2"', after=stop)
        player.start()

        logging.info("Started testing yt")

# End voice section

# End core bot

# Running the bot, continued

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)

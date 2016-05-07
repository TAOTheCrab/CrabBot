#!/usr/bin/env python3
# NOTE: using Python3.5+ async syntax
# Simple Discord chatbot for fun
#
# Requires a bot user token. See -h for details.

import asyncio
import discord
from discord.ext import commands
from pathlib import Path
import logging
import random

voice_enabled = True  # Set to False to disable voice commands

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!crab'),
                   description="Huh, another bot")


def run_bot(login):
    bot.run(login)  # WARNING blocking call


async def update_profile(username=None, avatar=None):
    if avatar is not None:
        # As far as I can tell, Discord's official API only supports JPEG
        new_avatar = open(picture, 'rb')
        picture_bits = new_avatar.read()
        new_avatar.close()
    await bot.edit_profile(username=username, avatar=picture_bits)
    logging.info("Updated profile")

# Running the bot

# TODO convert update_profile() to optional startup args (safer)
# PROBLEM can't currently update until logged in, but bot.run() is blocking
# SOLUTION? do the update in the poll thread (use terminal command instead?)

# End running the bot (more at end of file)

# Begin core bot stuff


def read_list_file(filepath):
    with filepath.open() as file_list:
        words = [x.rstrip() for x in file_list]
    # TODO check whether trailing newlines make it into the list as blank strings
    return words

# TODO make configurable
assets_path = Path("assets")
memes_path = Path("assets/memes")


def update_lists():
    # !dota
    global mobas
    mobas = read_list_file(assets_path / "mobas.txt")
    # !sir
    global places
    places = read_list_file(assets_path / "sir-places.txt")
    # !adventure
    global deaths
    deaths = read_list_file(assets_path / "adventure-deaths.txt")
    global killers
    killers = read_list_file(assets_path / "adventure-killers.txt")
    global locations
    locations = read_list_file(assets_path / "adventure-locations.txt")
    global rewards
    rewards = read_list_file(assets_path / "adventure-rewards.txt")
    # !cake
    global cakes
    cakes = read_list_file(assets_path / "cakes.txt")
    # !memes
    # TODO? instead, iterate over or choose from the contents of memes_path
    global the_memes
    the_memes = read_list_file(memes_path / "filelist.txt")

update_lists()  # Initialize the lists


def log_command(used):
    # TODO convert to Context.command. Set pass_context=True for all commands,
    # or look into overriding process_commands.
    # Probably not worth cluttering code further than just calls to logging.
    logging.info("Command: " + used)

# https://github.com/Rapptz/discord.py/blob/async/examples/basic_bot.py


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


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
    if random.randint(1, 10) == 5:  # 10%
        await bot.say("Ok")
    else:
        await bot.say("Help is transient, and for some reason is not provided here.")


@bot.command(help="👍")
async def thumbsup(num='1'):
    if num not in ('nope', '0'):
        try:
            number = int(num)
        except ValueError:
            number = 1
        await bot.reply("👍" * number)
    else:
        await bot.say("Awww")


@bot.command()
async def cake(num='1'):
    reply = [random.choice(cakes) for _ in range(abs(int(num)))]
    await bot.say(''.join(reply))


@bot.command(help="Go on a quest!")
async def adventure():
    await bot.say("Simulating adventure...")
    await bot.type()
    await asyncio.sleep(3)  # suspense!
    if random.randint(1, 10) == 5:  # 10% chance to win
        reward = random.choice(rewards)
        await bot.say("You win! You got {}!".format(reward))
    else:  # Ruin!
        death = random.choice(deaths)
        killer = random.choice(killers)
        location = random.choice(locations)
        await bot.say("You were {} by {} in {}".format(death, killer, location))

# Begin voice section

# https://github.com/Rapptz/discord.py/blob/async/examples/playlist.py

voice_connection = None
voice_player = None

async def connect_voice(ctx):
    # Might be nice to check if voice is True, but for now
    # disabling commands should be enough

    logging.info("Attempting a voice connection")

    user_channel = ctx.message.author.voice_channel
    if user_channel is None:
        logging.info("Voice connection aborted: User not in a channel")
        await bot.reply("Try being in a voice channel first")
        return

    # Needed for voice playback
    if not discord.opus.is_loaded():
        discord.opus.load_opus('opus')

    global voice_connection

    try:
        voice_connection = await bot.join_voice_channel(user_channel)
        logging.info("Voice connected to " + user_channel.name)
    except discord.ClientException as e:
        logging.info(e)


@bot.command()  # Doesn't hurt to keep enabled even if voice is False
async def stop_voice():
    global voice_player  # just to be explicit. Might want to set player to None later?

    logging.info("Attempting to stop voice")

    # TODO figure out global player (currently this is always None).
    # voice.disconnect() covers us, but...
    if voice_player is not None:
        voice_player.stop()
        logging.info("Voice player stopped")

    if bot.is_voice_connected(voice_connection.server):
        logging.info("Disconnecting from voice")
        await voice_connection.disconnect()
        logging.info("Voice disconnected")


@bot.command(enabled=voice_enabled, pass_context=True, help="Lost?")
async def memes(ctx):
    await connect_voice(ctx)

    # TODO figure out discord.py cogs (ext/commands/bot.py) for ex. player.stop()
    global voice_player  # in meantime global player var?
    voice_player = voice_connection.create_ffmpeg_player(
        str(memes_path) + '/' + random.choice(the_memes),
        options='-af "volume=0.2"',
        after=stop_voice)
    voice_player.start()

    logging.info("Started memes")


@bot.command(enabled=voice_enabled, pass_context=True,
             help="Plays most things supported by youtube-dl")
async def stream(ctx, video=None):
    await connect_voice(ctx)

    if video is not None:
        # TODO further testing. stop doesn't seem to trigger
        #      (might be computer-specific)
        global voice_player
        voice_player = await voice_connection.create_ytdl_player(
            video,
            options='-af "volume=0.2"',
            after=stop_voice)
        voice_player.start()

        logging.info("Started streaming")

# End voice section

# End core bot

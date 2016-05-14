#!/usr/bin/env python3
# NOTE: using Python3.5+ async syntax
# Simple Discord chatbot for fun
#
# Requires a bot user token. See -h for details.

import asyncio
import discord
from discord.ext import commands
import logging
from pathlib import Path
import random

bot = commands.Bot(command_prefix=commands.when_mentioned_or('!crab'),
                   description="Huh, another bot")

# bot.loop.set_debug(True)


def run_bot(login):
    bot.run(login)  # WARNING blocking call


async def update_profile(username=None, avatar=None):
    logging.info("Updating profile")

    # BUG using new_username seems to always return BAD REQUEST, disabled for now
    if username is not None:
        new_username = username
    else:
        new_username = bot.user.name

    # TODO convert to try: fields['avatar'] except KeyError, so we can use None for 'no avatar'
    if avatar is not None:
        # As far as I can tell, Discord's official API only supports JPEG
        new_avatar = open(avatar, 'rb')
        picture_bytes = new_avatar.read()
        new_avatar.close()
        await bot.edit_profile(username=username, avatar=picture_bytes)
    else:
        # edit_profile only skips bytes processing if avatar doesn't exist at all
        # BUG server returns BAD REQUEST
        await bot.edit_profile(username=new_username)

    logging.info("Profile updated")


def _update_profile(username=None, avatar=None):
    # Mostly for threads, to allow them to call the update_profile coroutine
    logging.info("Calling update_profile")
    up_function = update_profile(username, avatar)
    future = asyncio.run_coroutine_threadsafe(up_function, bot.loop)
    logging.info("update_profile completed with: " + str(future.exception()))


def read_list_file(filepath):
    with filepath.open() as file_list:
        words = [x.rstrip() for x in file_list]
    # TODO check whether trailing newlines make it into the list as blank strings
    return words

# TODO make configurable
assets_path = Path("assets")


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

# Helper functions for addon modules


def crabcommand(*args, **kwargs):
    ''' Register a bot command to CrabBot '''

    def decorator(func):
        bot.command(*args, **kwargs)(func)

    return decorator

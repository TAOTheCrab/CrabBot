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


def add_cog(cog, *args, **kwargs):
    bot.add_cog(cog(bot, *args, **kwargs))


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


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

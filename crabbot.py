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


class CrabBot(commands.Bot):
    def __init__(self, prefix='!crab'):
        super().__init__(command_prefix=commands.when_mentioned_or(prefix),
                         description="Huh, another bot")
        # loop.set_debug(True)  # Set asyncio loop to output more info for debugging
        # self.add_listener(self.on_ready)  # TIL on_ready in a Bot subclass is already registered

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def update_profile(self, username=None, avatar=None):
        logging.info("Updating profile")

        # BUG using new_username seems to always return BAD REQUEST, disabled for now
        if username is not None:
            new_username = username
        else:
            new_username = self.user.name

        # TODO convert to try: fields['avatar'] except KeyError, so we can use None for 'no avatar'
        if avatar is not None:
            # As far as I can tell, Discord's official API only supports JPEG
            new_avatar = open(avatar, 'rb')
            picture_bytes = new_avatar.read()
            new_avatar.close()
            await self.edit_profile(username=username, avatar=picture_bytes)
        else:
            # edit_profile only skips bytes processing if avatar doesn't exist at all
            # BUG server returns BAD REQUEST
            await self.edit_profile(username=new_username)

        logging.info("Profile updated")

    def _update_profile(self, username=None, avatar=None):
        # Mostly for threads, to allow them to call the update_profile coroutine
        logging.info("Calling update_profile")
        up_function = self.update_profile(username, avatar)
        future = asyncio.run_coroutine_threadsafe(up_function, self.loop)
        logging.info("update_profile completed with: " + str(future.exception()))


def read_list_file(filepath):
    with filepath.open() as file_list:
        words = [x.rstrip() for x in file_list]
    # TODO check whether trailing newlines make it into the list as blank strings
    return words

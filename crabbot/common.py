#!/usr/bin/env python3
# Simple Discord chatbot for fun
# Main bot management plus some functions common between command cogs.
#
# Requires a bot user token.

import asyncio
import logging
from pathlib import Path
import random

from discord.ext.commands import Bot as DiscordBot, when_mentioned_or


def read_list_file(filepath: Path):
    # Force utf-8, to be explicit/get Windows in line
    with filepath.open(encoding="utf-8") as file_list:
        words = [x.rstrip() for x in file_list]
    return words


class CrabBot(DiscordBot):
    def __init__(self, prefix='!crab'):
        # Could just use command_prefix arg, but this allows for a default prefix
        super().__init__(command_prefix=when_mentioned_or(prefix),
                         description="Huh, another bot")
        # loop.set_debug(True)  # Set asyncio loop to output more info for debugging
        # self.add_listener(self.on_ready)  # TIL on_ready in a Bot subclass is already registered

        self.cogs_update_lists = {}

    async def on_ready(self):
        login_msg = ('Logged in as {} ({})\n'.format(self.user.name, self.user.id) +
                     '------')

        print(login_msg)
        logging.info(login_msg)

    async def update_profile(self, username=None, avatar=None):
        logging.info("Updating profile")

        # TODO probably just convert this to require both args, since single arg seems too buggy
        # BUG using new_username seems to always return BAD REQUEST, disabled for now
        if username is not None:
            new_username = username
        else:
            new_username = self.user.name

        # TODO convert to try: fields['avatar'] except KeyError, so we can use None for 'no avatar'
        #      to signal edit_profile() to use the existing profile fields instead
        if avatar is not None:
            # Discord.py documents JPEG and PNG as supported.
            new_avatar = open(avatar, 'rb')
            picture_bytes = new_avatar.read()
            new_avatar.close()
            await self.user.edit(username=username, avatar=picture_bytes)
        else:
            # edit_profile only skips bytes processing if avatar doesn't exist at all
            # BUG server returns BAD REQUEST
            await self.user.edit(username=new_username)

        logging.info("Profile updated")

    def _update_profile(self, username=None, avatar=None):
        # Mostly for threads, to allow them to call the update_profile coroutine
        logging.info("Calling update_profile")
        up_function = self.update_profile(username, avatar)
        future = asyncio.run_coroutine_threadsafe(up_function, self.loop)
        logging.info("update_profile completed with: " + str(future.exception()))

    def update_all_lists(self):
        for cog_name, cog_function in self.cogs_update_lists.items():
            cog_function()
            logging.info("Updated lists for {}".format(cog_name))

    def add_cog(self, cog):
        super(CrabBot, self).add_cog(cog)
        logging.info("Added cog {}".format(cog.__class__.__name__))
        if hasattr(cog, "update_lists"):
            self.cogs_update_lists[cog.__class__.__name__] = cog.update_lists

    def remove_cog(self, cog_name):
        super(CrabBot, self).remove_cog(cog_name)
        logging.info("Removed cog {}".format(cog_name))
        if cog_name in self.cogs_update_lists:
            del self.cogs_update_lists[cog_name]

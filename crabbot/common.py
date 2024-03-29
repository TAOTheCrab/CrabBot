#!/usr/bin/env python3
# Simple Discord chatbot for fun
# Main bot management plus some functions common between command cogs.
#
# Requires a bot user token.

import asyncio
import logging
from pathlib import Path
import random

import discord
from discord.ext.commands import Bot as DiscordBot, when_mentioned_or

log = logging.getLogger(__name__)

def read_list_file(filepath: Path):
    # Force utf-8, to be explicit/get Windows in line
    with filepath.open(encoding="utf-8") as file_list:
        words = [x.rstrip() for x in file_list]
    return words


# We're treating these as default CrabBot cogs (though honestly it's just to show/test how to add cogs in init)
# TODO might want to only add messages by default, it's the most used and the least likely to be busted.
from .cogs import messages, quotes

class CrabBot(DiscordBot):
    ''' The heart of CrabBot. 

    Default paths assume the bot is being run at project root (eg. as crabbot.common.CrabBot()).
    '''

    def __init__(self, prefix='!crab', 
                       assets_path: Path = Path("assets"), 
                       quotes_path: Path = Path("..")):
        # Could just use command_prefix arg, but this allows for a default prefix
        # TODO (new in Discord.py 1.5) determine what Intents we need https://discordpy.readthedocs.io/en/latest/intents.html
        #      CrabBot should be functional with the default Intents, but we might be able to opt out of some.
        #      THOUGHT: should we process cogs first, or acknowledge that cogs will require the host bot to subscribe to Intents on their behalf?
        # For now just use the default intents, now that they're required to be explicit in discord.py v2
        crabbot_intents = discord.Intents.default()
        super().__init__(intents=crabbot_intents,
                         command_prefix=when_mentioned_or(prefix),
                         description="Huh, another bot")
        # loop.set_debug(True)  # Set asyncio loop to output more info for debugging
        # self.add_listener(self.on_ready)  # TIL on_ready in a Bot subclass is already registered

        self.cogs_update_lists: dict = {}

        # TODO? Be able to reconfigure this live. Should probably add a function to the cogs too rather than reloading them.
        self.assets_path = assets_path
        self.quotes_path = quotes_path

    async def setup_hook(self):
        # Add default cogs
        await self.add_cog(messages.Messages(self.assets_path / "messages"))
        await self.add_cog(quotes.Quotes(self.quotes_path))

    async def on_ready(self):
        # Register the new cog commands with slash commands
        await self.tree.sync()

        login_msg = ('Logged in as {} ({})\n'.format(self.user.name, self.user.id) +
                     '------')

        print(login_msg)
        log.info(login_msg)

    async def update_profile(self, username=None, avatar=None):
        log.info("Updating profile")

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

        log.info("Profile updated")

    def _update_profile(self, username=None, avatar=None):
        # Mostly for threads, to allow them to call the update_profile coroutine
        log.info("Calling update_profile")
        up_function = self.update_profile(username, avatar)
        future = asyncio.run_coroutine_threadsafe(up_function, self.loop)
        log.info("update_profile completed with: " + str(future.exception()))

    def update_all_lists(self):
        for cog_name, cog_function in self.cogs_update_lists.items():
            cog_function()
            log.info("Updated lists for {}".format(cog_name))

    async def add_cog(self, cog):
        await super(CrabBot, self).add_cog(cog)
        log.info("Added cog {}".format(cog.__class__.__name__))
        if hasattr(cog, "update_lists"):
            self.cogs_update_lists[cog.__class__.__name__] = cog.update_lists

    async def remove_cog(self, cog_name):
        await super(CrabBot, self).remove_cog(cog_name)
        log.info("Removed cog {}".format(cog_name))
        if cog_name in self.cogs_update_lists:
            del self.cogs_update_lists[cog_name]

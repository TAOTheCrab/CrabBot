#!/usr/bin/env python3
# CrabBot quotes
#
# Partially inspired by LRRBot

import discord
from discord.ext import commands
import json
import logging
from pathlib import Path
import random
# import sqlite3  # Leaving as a note of possible db alternatives


class Quotes:

    def __init__(self, bot, quotes_db_path):
        self.bot = bot
        self.quotes_db_path = Path(quotes_db_path)
        self.quotes = None

        # Load the db into memory
        # NOTE currently CrabBot does not have a mechanism for shutting down gracefully
        #      so for now we're gonna jsut write out changes whenever they happen
        with self.quotes_db_path.open() as f:  # TODO file open error checking
            self.quotes = json.load(f)

    @commands.group(pass_context=True,
                    help=('Read or add quotes! See "help quotes" for details\n'
                          'New quote: quotes [name] "Insert quote here!"\n'
                          'Get random quote: quotes [name]'))
    async def quote(self, ctx):
        if ctx.invoked_subcommand is not None:
            return

        await self.bot.say("Be more quotable, then maybe we'd finish this command. :neutral_face:")

        '''
        # Might want to remove this if "quotes quotes" is a problem
        if not query.lower().startswith("quotes"):
            return

        # Same here
        query = query[6:].strip()

        name = query.split("\"")[0].strip()
        query = query.replace(name, "").replace("\"", "").strip()

        if query == "":
            await self.bot.say(random.choice(quotes[name]))
            return

        if name not in quotes:
            quotes[name] = []

        if query not in quotes[name]:
            quotes[name].append(query)
            await self.bot.say("Added quote for " + name + ".")

        with self.quotes_db_path.open() as f:
            json.dump(quotes, f)
        '''

    @quote.command()
    async def add(self, name, quote):
        await self.bot.say('Sorry {name}, we cannot add the quote "{quote}" due to oppressive overlords.'.format(name=name, quote=quote))

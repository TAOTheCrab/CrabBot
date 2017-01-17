#!/usr/bin/env python3
# CrabBot quotes
#
# Partially inspired by LRRBot

'''
JSON format
{
    Name1: [
        "Quote1"
        "Quote2"
        ...
    ],
    Name2: [
    ...
'''

import json
from pathlib import Path
import random
# import sqlite3  # Leaving as a note of possible db alternatives

from discord.ext import commands


class Quotes:

    def __init__(self, bot, quotes_db_path):
        self.bot = bot
        self.quotes_db_path = Path(quotes_db_path)
        self.quotes = {}  # Fallback quote initialization TODO: check what we want initialized

        # Load the db into memory
        # NOTE currently CrabBot does not have a mechanism for shutting down gracefully
        #      so for now we're gonna just write out changes whenever they happen
        if self.quotes_db_path.exists():
            # TODO JSON error checking
            with self.quotes_db_path.open() as f:
                self.quotes = json.load(f)

    @commands.group(pass_context=True,
                    help=('Read or add quotes! See "help quote" for details\n'
                          '\n'
                          'If no command is given, a random quote is printed'))
    async def quote(self, ctx):
        if ctx.invoked_subcommand is not None:
            return

        # await self.bot.say("Be more quotable, then maybe we'd finish this command. :neutral_face:")

        # TODO consider using name.lower() to standardize input. Or some kind of fuzzy matching.

        # TODO do something different to get names, currently spaces are ignored
        name = ctx.subcommand_passed  # attempt to get the rest of the message

        if name is None:
            name = random.choice(list(self.quotes.keys()))

        # TODO if name is "", pick any old random quote

        if name in self.quotes:
            selected_quote = random.choice(self.quotes[name])
            await self.bot.say("{quote} \n  —{name}".format(quote=selected_quote, name=name))
        else:
            await self.bot.say("No quotes from {name}".format(name=name))

    @quote.command(help='List all authors of recorded quotes')
    async def authors(self):
        authors = self.quotes.keys()
        await self.bot.say(";  ".join(authors))

    @quote.command(help=('Add a quote.\n'
                         'Say the name of the person being quoted, then '
                         'write the quote in quotation marks.\n'
                         'eg. quote add Steve "Steve said this thing"\n'
                         '\n'
                         'You can also put quotation marks around the author to add a name with spaces'))
    async def add(self, name, quote):
        # Testing code
        # await self.bot.say('Sorry {name}, we cannot add the quote "{quote}" due to oppressive overlords.'.format(name=name, quote=quote))

        # TODO think about data structure. Would kind of like to number quote for reference purposes.
        # TODO? allow use of @User id numbers instead of hardcoded names
        #       problem: using @User notifies user of the message
        #       Try to match string name with in-server user and store their ID for later matching?

        # TODO consider using name.lower() to standardize input

        if name not in self.quotes:
            self.quotes[name] = []

        if quote not in self.quotes[name]:
            self.quotes[name].append(quote)
            await self.bot.say("Quote added")

        # NOTE: We're being somewhat unsafe by overwriting this all the time.
        #       Have to reboot CrabBot to actually load this.
        with self.quotes_db_path.open('w') as f:  # Remove if graceful shutdown and/or autosave is implemented
            json.dump(self.quotes, f)

    # TODO 'remove' command

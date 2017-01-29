#!/usr/bin/env python3
# CrabBot quotes
#
# Partially inspired by LRRBot

'''
SQL format
Table "quotes"
    author: text
    quote: text
'''

from pathlib import PurePath
import random
import sqlite3

from discord.ext import commands


class Quotes:

    def __init__(self, bot, quotes_db_path):
        self.bot = bot
        self.quotes_db_path = PurePath(quotes_db_path)

        # TODO SQL error handling (applies to most of this module)
        self.quotes_db_connection = sqlite3.connect(str(self.quotes_db_path / "quotes.sqlite3"))
        self.quotes_db_cursor = self.quotes_db_connection.cursor()
        self.quotes_db_cursor.execute("CREATE TABLE IF NOT EXISTS quotes "
                                      "(author text NOT NULL, quote text NOT NULL)")

    @commands.group(pass_context=True, invoke_without_command=True,
                    help=('Read or add quotes! See "help quote" for details\n'
                          '\n'
                          'If no command is given, a random quote is printed'))
    async def quote(self, ctx, *, name=None):
        # TODO consider using name.lower() to standardize input. Or some kind of fuzzy matching.

        self.quotes_db_cursor.execute("SELECT DISTINCT author FROM quotes")
        # DB query result is a list of 1-tuples, so we extract the contained strs
        authors = [x[0] for x in self.quotes_db_cursor.fetchall()]

        if name is None:  # User wants any random quote, so we pick an author
            name = random.choice(authors)

        if name in authors:
            self.quotes_db_cursor.execute("SELECT quote FROM quotes "
                                          "WHERE author IS ? "
                                          "ORDER BY RANDOM()"
                                          "LIMIT 1", (name,))
            # Just escape one 1-tuple. We already have the name, so meh.
            selected_quote = self.quotes_db_cursor.fetchone()[0]
            await self.bot.say("{quote} \n  —{name}".format(quote=selected_quote,
                                                            name=name))
        else:
            await self.bot.say("No quotes from {name}.".format(name=name))

    @quote.command(help='List all authors of recorded quotes')
    async def authors(self):
        self.quotes_db_cursor.execute("SELECT DISTINCT author FROM quotes "
                                      "ORDER BY author COLLATE NOCASE")
        # DB query result is a list of 1-tuples, so we extract the contained strs
        authors = [x[0] for x in self.quotes_db_cursor.fetchall()]

        await self.bot.say(";  ".join(authors))

    @quote.command(help='Search for a random quote with the given string in it.\n'
                        '\n'
                        'Only searches quote contents and returns word-for-word matches.\n'
                        'Not case sensitive.')
    async def search(self, *, query: str):
        ''' Get a random quote containing the word-for-word query in it'''
        # LIKE is case-insensitive for ASCII-range letters only.
        #   Also, it is claimed LIKE is slow for searches starting with %,
        #   so maybe keep an eye out if it becomes a problem.
        #   There are the SQLite FTS extensions, but they're not enabled by default.
        self.quotes_db_cursor.execute("SELECT * FROM quotes "
                                      "WHERE quote LIKE ? "
                                      "ORDER BY RANDOM() "
                                      "LIMIT 1", ('%' + query + '%',))
        quote = self.quotes_db_cursor.fetchone()

        if quote is None:
            await self.bot.say("No quotes found.")
        else:
            await self.bot.say("{quote} \n  —{name}".format(quote=quote[1],
                                                            name=quote[0]))

    @quote.command(help=('Add a quote.\n'
                         'Say the name of the person being quoted, then '
                         'write the quote (quotation marks are optional).\n'
                         'eg. quote add Steve "Steve said this thing"\n'
                         '\n'
                         'To add a name with spaces in it, you must put the name in quotation marks.'))
    async def add(self, name: str, *, quote: str):
        # TODO Would kind of like to number quote for reference purposes.
        # TODO? allow use of @User id numbers instead of hardcoded names
        #       problem: using @User notifies user of the message
        #       Try to match string name with in-server user and store their ID for later matching?

        # NOTE: For capitalization sanitation, there's 'author COLLATE NOCASE'
        #       either in CREATE TABLE or 'SELECT DISTINCT author COLLATE NOCASE'
        #       Both ways, 'quote name' will probably need a couple tolower()s

        # TODO error handling.
        self.quotes_db_cursor.execute("INSERT INTO quotes VALUES "
                                      "(?,?)", (name, quote))

        # For safety (CrabBot has no graceful shutdown), just write the changes now
        self.quotes_db_connection.commit()

        await self.bot.say("Quote added.")

    # TODO 'remove' command

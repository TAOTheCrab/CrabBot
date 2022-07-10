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

import discord
from discord.app_commands import command
from discord.ext.commands import GroupCog


class Quotes(GroupCog):

    def __init__(self, quotes_db_path):
        self.quotes_db_path = PurePath(quotes_db_path)

        # TODO SQL error handling (applies to most of this module)
        self.quotes_db_connection = sqlite3.connect(str(self.quotes_db_path / "quotes.sqlite3"))
        self.quotes_db_cursor = self.quotes_db_connection.cursor()
        self.quotes_db_cursor.execute("CREATE TABLE IF NOT EXISTS quotes "
                                      "(author text NOT NULL, quote text NOT NULL)")

    def __unload(self):
        # This is mostly just to express that we definitely want everything cleaned up on unload
        # and a reminder that unload exists if we want to, say, commit beforehand.
        self.quotes_db_cursor.close()
        self.quotes_db_connection.close()

    @command(description=("Grab a quote."
                          'If no name is given, a random quote is printed'))
    async def quote(self, interaction: discord.Interaction, name : str =None):
        # TODO consider using name.lower() to standardize input. Or some kind of fuzzy matching.

        self.quotes_db_cursor.execute("SELECT DISTINCT author FROM quotes")
        # DB query result is a list of 1-tuples, so we extract the contained strs
        authors = [x[0] for x in self.quotes_db_cursor.fetchall()]

        # Bail out if there are no entries at all
        if not authors:
            # BUG The implication of per-server quotes is a hopeful lie to get me to actually implement them.
            await interaction.response.send_message(f"This server has no quotes. Add some with `quote add`.")
            return

        if name is None:  # User wants any random quote, so we pick an author
            # BUG if quotes db is empty, this errors out silently. Need to inform user.
            name = random.choice(authors)

        if name in authors:
            self.quotes_db_cursor.execute("SELECT quote FROM quotes "
                                          "WHERE author IS ? "
                                          "ORDER BY RANDOM()"
                                          "LIMIT 1", (name,))
            # Just escape one 1-tuple. We already have the name, so meh.
            selected_quote = self.quotes_db_cursor.fetchone()[0]
            await interaction.response.send_message(f"{selected_quote} \n  —{name}")
        else:
            await interaction.response.send_message(f"No quotes from {name}.")

    @command(description='List all authors of recorded quotes')
    async def authors(self, interaction: discord.Interaction):
        self.quotes_db_cursor.execute("SELECT DISTINCT author FROM quotes "
                                      "ORDER BY author COLLATE NOCASE")
        # DB query result is a list of 1-tuples, so we extract the contained strs
        authors = [x[0] for x in self.quotes_db_cursor.fetchall()]

        await interaction.response.send_message(";  ".join(authors))

    @command(description='Search for a random quote with the given string in it.\n')
    async def search(self, interaction: discord.Interaction, query: str):
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
            await interaction.response.send_message("No quotes found.")
        else:
            await interaction.response.send_message(f"{quote[1]} \n  —{quote[0]}")

    @command(description='Add a quote.\n')
    async def add(self, interaction: discord.Interaction, name: str, quote: str):
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

        await interaction.response.send_message("Quote added.")

    # TODO 'remove' command

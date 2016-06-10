#!/usr/bin/env python3
# CrabBot general message commands (mostly fun phrasal template responses)

import asyncio
import discord
from discord.ext import commands
import logging
from pathlib import Path
import random

import crabbot.common


class Messages(crabbot.common.CrabBotCog):
    has_lists = True

    def __init__(self, bot, assets_path):
        super().__init__(bot)

        self.assets_path = Path(assets_path)
        # Initialize the lists
        self.update_lists()

    def update_lists(self):
        # !dota
        self.mobas = crabbot.common.read_list_file(self.assets_path / "mobas.txt")
        # !sir
        self.sirplaces = crabbot.common.read_list_file(self.assets_path / "sir-places.txt")
        # !adventure
        self.deaths = crabbot.common.read_list_file(self.assets_path / "adventure-deaths.txt")
        self.killers = crabbot.common.read_list_file(self.assets_path / "adventure-killers.txt")
        self.locations = crabbot.common.read_list_file(self.assets_path / "adventure-locations.txt")
        self.rewards = crabbot.common.read_list_file(self.assets_path / "adventure-rewards.txt")
        # !cake
        self.cakes = crabbot.common.read_list_file(self.assets_path / "cakes.txt")
        # !band
        self.bandadjectives = crabbot.common.read_list_file(self.assets_path / "band-adjectives.txt")
        self.bandnouns = crabbot.common.read_list_file(self.assets_path / "band-nouns.txt")
        self.bandplaces = crabbot.common.read_list_file(self.assets_path / "band-places.txt")
        # !band style
        self.bandstyles = crabbot.common.read_list_file(self.assets_path / "band-styles.txt")

    @commands.command(help='The bots have something to say')
    async def takeover(self):
        await self.bot.say("Something something robots")

    @commands.command(help='Well, what is this Lords Management then?', aliases=['lol'])
    async def dota(self):
        moba = random.choice(self.mobas)
        await self.bot.say("This is a strange {} mod".format(moba))

    @commands.command(enabled=True, hidden=True)
    async def annoy(self):
        # TODO anti-spam cooldown (probably a good idea for most commands)
        await self.bot.say("Ho ho ha ha!", tts=True)

    @commands.command(help='For the unruly patron')
    async def sir(self):
        # Yes, possibly having repeats is intentional, more fun that way
        place_one = random.choice(self.sirplaces)
        place_two = random.choice(self.sirplaces)
        reply = "Sir, this is {}, not {}.".format(place_one, place_two)
        await self.bot.say(reply)

    @commands.command()
    async def assist(self):
        if random.randint(1, 10) == 5:  # 10%
            await self.bot.say("Ok")
        else:
            await self.bot.say("Help is transient, and for some reason is not provided here.")

    @commands.command(help="👍")
    async def thumbsup(self, num='1'):
        if num not in ('nope', '0'):
            try:
                number = int(num)
            except ValueError:
                number = 1
            await self.bot.reply("👍" * number)
        else:
            await self.bot.say("Awww")

    @commands.command()
    async def cake(self, num='1'):
        reply = [random.choice(self.cakes) for _ in range(abs(int(num)))]
        await self.bot.say(''.join(reply))

    @commands.command(help="Go on a quest!")
    async def adventure(self):
        await self.bot.say("Simulating adventure...")
        await self.bot.type()
        await asyncio.sleep(3)  # suspense!
        if random.randint(1, 10) == 5:  # 10% chance to win
            reward = random.choice(self.rewards)
            await self.bot.say("You win! You got {}!".format(reward))
        else:  # Ruin!
            death = random.choice(self.deaths)
            killer = random.choice(self.killers)
            location = random.choice(self.locations)
            await self.bot.say("You were {} by {} in {}".format(death, killer, location))

    @commands.group(help="Need a band name?")
    async def band(self):
        adjective = random.choice(self.bandadjectives)
        noun = random.choice(self.bandnouns)
        place = random.choice(self.bandplaces)
        await self.bot.say("Your new band name is {} {} {}".format(adjective, noun, place))

    @band.command(name="style")
    async def _style(self):
        style = random.choice(self.bandstyles)
        await self.bot.say("    which is a {} cover band.".format(style))

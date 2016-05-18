#!/usr/bin/env python3

import crabbot

import asyncio
import discord
from discord.ext import commands
import logging
from pathlib import Path
import random


class Messages:
    def __init__(self, bot):
        # TODO make configurable (class arg?)
        self.assets_path = Path("assets")
        # Initialize the lists
        self.update_messages_lists()

        self.bot = bot

    def update_messages_lists(self):
        # !dota
        self.mobas = crabbot.read_list_file(self.assets_path / "mobas.txt")
        # !sir
        self.places = crabbot.read_list_file(self.assets_path / "sir-places.txt")
        # !adventure
        self.deaths = crabbot.read_list_file(self.assets_path / "adventure-deaths.txt")
        self.killers = crabbot.read_list_file(self.assets_path / "adventure-killers.txt")
        self.locations = crabbot.read_list_file(self.assets_path / "adventure-locations.txt")
        self.rewards = crabbot.read_list_file(self.assets_path / "adventure-rewards.txt")
        # !cake
        self.cakes = crabbot.read_list_file(self.assets_path / "cakes.txt")

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
        place_one = random.choice(self.places)
        place_two = random.choice(self.places)
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

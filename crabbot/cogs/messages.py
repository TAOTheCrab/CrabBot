#!/usr/bin/env python3
# CrabBot general message commands (mostly fun phrasal template responses)

import asyncio
from pathlib import Path
import random

import discord
from discord.ext.commands import Cog, command, group

from crabbot.common import read_list_file


class Messages(Cog):
    def __init__(self, assets_path):
        self.spam_limit = 100  # Limit for repetitive emotes commands

        self.assets_path = Path(assets_path)
        # Initialize the lists
        self.update_lists()

    def update_lists(self):
        # !dota
        self.mobas = read_list_file(self.assets_path / "mobas.txt")
        # !sir
        self.sirplaces = read_list_file(self.assets_path / "sir-places.txt")
        # !adventure
        self.deaths = read_list_file(self.assets_path / "adventure-deaths.txt")
        self.killers = read_list_file(self.assets_path / "adventure-killers.txt")
        self.locations = read_list_file(self.assets_path / "adventure-locations.txt")
        self.rewards = read_list_file(self.assets_path / "adventure-rewards.txt")
        # !cake
        self.cakes = read_list_file(self.assets_path / "cakes.txt")
        # !band
        self.bandadjectives = read_list_file(self.assets_path / "band-adjectives.txt")
        self.bandnouns = read_list_file(self.assets_path / "band-nouns.txt")
        self.bandplaces = read_list_file(self.assets_path / "band-places.txt")
        # !band style
        self.bandstyles = read_list_file(self.assets_path / "band-styles.txt")
        # !world
        self.worldwords = read_list_file(self.assets_path / "world-words.txt")

    @command(help='The bots have something to say')
    async def takeover(self, ctx):
        await ctx.send("Something something robots")

    @command(aliases=['lol'], help='Well, what is this Lords Management then?')
    async def dota(self, ctx):
        moba = random.choice(self.mobas)
        await ctx.send(f"This is a strange {moba} mod")

    @command(enabled=True, hidden=True)
    async def annoy(self, ctx):
        # TODO anti-spam cooldown (probably a good idea for most commands)
        await ctx.send("Ho ho ha ha!", tts=True)

    @command(help='For the unruly patron')
    async def sir(self, ctx):
        # Yes, possibly having repeats is intentional, more fun that way
        place_one = random.choice(self.sirplaces)
        place_two = random.choice(self.sirplaces)
        await ctx.send(f"Sir, this is {place_one}, not {place_two}.")

    @command()
    async def assist(self, ctx):
        if random.randint(1, 10) == 5:  # 10%
            await ctx.send("Ok")
        else:
            await ctx.send("Help is transient, and for some reason is not provided here.")

    @command(help="👍")
    async def thumbsup(self, ctx, num='1'):
        if num not in ('nope', '0'):
            try:
                number = int(num)
                if number > self.spam_limit:
                    number = self.spam_limit
            except ValueError:
                number = 1
            await ctx.send(f"{ctx.author.mention} {'👍' * number}")
        else:
            await ctx.send("Awww")

    @command()
    async def cake(self, ctx, num='1'):
        try:
            number = int(num)
            if number > self.spam_limit:
                number = self.spam_limit
        except ValueError:
            number = 1
        reply = [random.choice(self.cakes) for _ in range(abs(int(num)))]
        await ctx.send(''.join(reply))

    @command(help="Go on a quest!")
    async def adventure(self, ctx):
        await ctx.send("Simulating adventure...")
        async with ctx.typing():
            await asyncio.sleep(3)  # suspense!
            if random.randint(1, 10) == 5:  # 10% chance to win
                reward = random.choice(self.rewards)
                await ctx.send(f"You win! You got {reward}!")
            else:  # Ruin!
                death = random.choice(self.deaths)
                killer = random.choice(self.killers)
                location = random.choice(self.locations)
                await ctx.send(f"You were {death} by {killer} in {location}")

    @group(help="Need a band name?")
    async def band(self, ctx):
        adjective = random.choice(self.bandadjectives)
        noun = random.choice(self.bandnouns)
        place = random.choice(self.bandplaces)
        await ctx.send(f"Your new band name is {adjective} {noun} {place}")

    @band.command()
    async def style(self, ctx):
        style = random.choice(self.bandstyles)
        await ctx.send(f"which is a {style} cover band.")

    @command(aliases=['world', 'planet'], help="Name a new Land! Thanks, Homestuck!")
    async def land(self, ctx):
        # Repeat words are OK
        word1 = random.choice(self.worldwords)
        word2 = random.choice(self.worldwords)
        # Might have to watch this one for iffy combos
        abbreviation = f"LO{word1[0]}A{word2[0]}"
        await ctx.send(f"Land of {word1} and {word2}   ({abbreviation})")

    # TODO figure out how to make commands with spaces. Probably have to just do SUMMON @group() somehow tho.
    @command(aliases=['SUMMON THE BEAR'], help="SUMMON THE BEAR")
    async def BEAR(self, ctx):
        ''' SUMMON THE BEAR '''

        # Alt. upload version. Bad for slow upload speeds. Also maybe don't fill Discord with 100s of bear gif files?
        # await ctx.send(file=discord.File(str(self.assets_path / "SUMMONTHEBEAR.gif")))

        emoji_bear = discord.utils.get(ctx.message.guild.emojis, name="bearmoji")
        # print(f"{type(emoji_bear)} : {emoji_bear}")
        if emoji_bear is None:
            # Fallback unicode bear
            emoji_bear = "🐻"
        
        await ctx.send(emoji_bear)

    @command(help=("(Sauce by Captain_Siix (Twitter/Twitch))"))
    async def arc(self, ctx):
        ''' Server in-joke memes. The source file is being kept separately. '''

        # Well, screw it, this meme'll work until this link dies, lol. Don't want to upload it every time.
        await ctx.send("https://cdn.discordapp.com/attachments/452175328148979713/583852441519390740/arc_warden.mp4")

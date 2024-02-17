#!/usr/bin/env python3
# CrabBot general message commands (mostly fun phrasal template responses)

import asyncio
from pathlib import Path
import random
from typing import Literal

import discord
from discord.app_commands import command  # Not sure why Mypy doesn't think this should accept self, it's in the docs specifically
from discord.ext.commands import Cog

from crabbot.common import read_list_file


class Messages(Cog):
    def __init__(self, assets_path : Path):
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
        # !newthing
        self.newthingwords = read_list_file(self.assets_path / "newthing-words.txt")

    @command(description='The bots have something to say') # type: ignore
    async def takeover(self, interaction: discord.Interaction):
        await interaction.response.send_message("Something something robots")

    @command(description='Well, what is this Lords Management then?') # type: ignore
    async def dota(self, interaction: discord.Interaction):
        moba = random.choice(self.mobas)
        await interaction.response.send_message(f"This is a strange {moba} mod")

    @command(description='For the unruly patron') # type: ignore
    async def sir(self, interaction: discord.Interaction):
        # Yes, possibly having repeats is intentional, more fun that way
        place_one = random.choice(self.sirplaces)
        place_two = random.choice(self.sirplaces)
        await interaction.response.send_message(f"Sir, this is {place_one}, not {place_two}.")

    @command() # type: ignore
    async def assist(self, interaction: discord.Interaction):
        if random.randint(1, 10) == 5:  # 10%
            await interaction.response.send_message("Ok")
        else:
            await interaction.response.send_message("Help is transient, and for some reason is not provided here.")

    @command(description="👍") # type: ignore
    async def thumbsup(self, interaction: discord.Interaction, number: int = 1):
        if number > 0:
            if number > self.spam_limit:
                number = self.spam_limit

            await interaction.response.send_message(f"{interaction.user.mention} {'👍' * number}")
        else:
            await interaction.response.send_message("Awww")

    @command() # type: ignore
    async def cake(self, interaction: discord.Interaction, number: int = 1):
        if number > self.spam_limit:
            number = self.spam_limit

        reply = [random.choice(self.cakes) for _ in range(abs(number))]
        await interaction.response.send_message(''.join(reply))

    @command(description="Go on a quest!") # type: ignore
    async def adventure(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True)
        await asyncio.sleep(3)  # suspense!
        if random.randint(1, 10) == 5:  # 10% chance to win
            reward = random.choice(self.rewards)
            await interaction.followup.send(f"You win! You got {reward}!")
        else:  # Ruin!
            death = random.choice(self.deaths)
            killer = random.choice(self.killers)
            location = random.choice(self.locations)
            await interaction.followup.send(f"You were {death} by {killer} in {location}")

    # NOTE style is left over from when band was a test of Group subcommands, moreso than an actual good idea (thus it is default now).
    #      I thought maybe the Literal transformer would cause Discord to present it similarly (it doesn't, but you can at least type style if you want now), 
    #      but it does open the possibility of having style modifiers, so this awkward version will stay as an example
    @command(description="Need a band name?") # type: ignore
    async def band(self, interaction: discord.Interaction, style : Literal["style", "none"] = "style"):
        adjective = random.choice(self.bandadjectives)
        noun = random.choice(self.bandnouns)
        place = random.choice(self.bandplaces)
        message = f"Your new band name is {adjective} {noun} {place}"
        if style == "style":
            bandstyle = random.choice(self.bandstyles)
            message += f"\nwhich is a {bandstyle} cover band."
        await interaction.response.send_message(message)

    @command(description="Name a new Land! Thanks, Homestuck!") # type: ignore
    async def land(self, interaction: discord.Interaction):
        # Repeat words are OK
        word1 = random.choice(self.worldwords)
        word2 = random.choice(self.worldwords)
        # Might have to watch this one for iffy combos
        abbreviation = f"LO{word1[0]}A{word2[0]}"
        await interaction.response.send_message(f"Land of {word1} and {word2}   ({abbreviation})")

    # TODO figure out how to make commands with spaces. Probably have to just do SUMMON @group() somehow tho.
    @command(description="SUMMON THE BEAR") # type: ignore
    async def bear(self, interaction: discord.Interaction):
        ''' SUMMON THE BEAR '''

        # Alt. upload version. Bad for slow upload speeds. Also maybe don't fill Discord with 100s of bear gif files?
        # await ctx.send(file=discord.File(str(self.assets_path / "SUMMONTHEBEAR.gif")))

        emoji_bear = discord.utils.get(interaction.guild.emojis, name="bearmoji") # type: ignore
        # print(f"{type(emoji_bear)} : {emoji_bear}")
        if emoji_bear is None:
            # Fallback unicode bear
            emoji_bear = "🐻"
        
        await interaction.response.send_message(emoji_bear)

    @command(description=("(Sauce by Captain_Siix (Twitter/Twitch))")) # type: ignore
    async def arc(self, interaction: discord.Interaction):
        ''' Server in-joke memes. The source file is being kept separately. '''

        # Well, screw it, this meme'll work until this link dies, lol. Don't want to upload it every time.
        await interaction.response.send_message("https://cdn.discordapp.com/attachments/452175328148979713/583852441519390740/arc_warden.mp4")

    @command(description="Idea of the day") # type: ignore
    async def newthing(self, interaction: discord.Interaction, who: str = "Muddy"):
        action = "playing"  # TODO Would like to randomize this, but weighted towards "play" since that's the main idea
        chosennewthing = random.choice(self.newthingwords)
        
        await interaction.response.send_message(f"{who} wants to try {action} {chosennewthing}")
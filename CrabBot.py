#!/usr/bin/env python3
# NOTE: using Python3.5+ async syntax
# Simple Discord chatbot for fun
#
# Requires user.cfg with valid username/password combo

import discord
from discord.ext import commands
import random
import logging

bot = commands.Bot(command_prefix='!crab', description="Huh, another bot")

# TODO It would probably be nicer to store these somewhere else
mobas = ["Smite", "SMNC", "Strife", "Overwatch", "HoN", "AoS", "HotS"]
places = ["Desert Bus", "the woods", "a Discord server", "DotA", "a video game",
            "a hall of Ricks", "an interdimensional peace zone", "the TARDIS",
            "Twitch chat", "Dark Souls", "Stack Overflow"]

logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(help='The bots have something to say')
async def takeover():
    await bot.say("Something something robots")

@bot.command(help='Well, what is this Lords Management then?', aliases=['lol'])
async def dota():
    num = random.randint(1, (len(mobas) - 1))
    await bot.say("This is a strange {} mod".format(mobas[num]))

@bot.command(enabled=False, hidden=True)
async def annoy():
    # TODO anti-spam cooldown (probably a good idea for most commands)
    # NOTE so far untested with bot.say version, unsure if tts works
    await bot.say("Ho ho ha ha!", tts=True)

@bot.command(help='For the unruly patron')
async def sir():
    # Yes, possibly having repeats is intentional, more fun that way
    placeOne = random.randint(1, (len(places) - 1))
    placeTwo = random.randint(1, (len(places) - 1))
    reply = "Sir, this is {}, not {}.".format(places[placeOne], places[placeTwo])
    await bot.say(reply)

@bot.command()
async def assist():
    await bot.say("Help is transient, and for some reason is not provided here.")

@bot.command()
async def thumbsup():
    await bot.reply("👍")

# IMPROVEMENT give option to use args instead of cfg file
# if __name__ == "__main__":

user_config = open('user.cfg', 'r')
# TODO probably define a better cfg layout than username\n password
username = user_config.readline()
password = user_config.readline()
user_config.close()

username = username.strip('\n\r')
password = password.strip('\n\r')

bot.run(username, password)

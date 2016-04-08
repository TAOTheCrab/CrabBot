#!/usr/bin/env python3
# Simple Discord chatbot for fun
#
# Requires user.cfg with valid username/password combo

import discord
import asyncio
import random
import logging

client = discord.Client()

# TODO It would probably be nicer to store these somewhere else
mobas = ["Smite", "SMNC", "Strife", "Overwatch", "HoN", "AoS", "HotS"]
places = ["Desert Bus", "the woods", "a Discord server", "DotA", "a video game",
            "a hall of Ricks", "an interdimensional peace zone", "the TARDIS"
            "Twitch chat", "Dark Souls", "Stack Overflow"]

logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    # TODO look into better startswith processing (@bot.command ?)
    if message.content.startswith('!takeover'):
        await client.send_message(message.channel, "Something something robots")

    elif message.content.startswith('!dota') or message.content.startswith('!lol'):
        num = random.randint(1, (len(mobas) - 1))
        await client.send_message(message.channel, "This is a strange {} mod".format(mobas[num]))


    #elif message.content.startswith('!annoy'):
        # TODO anti-spam cooldown (probably a good idea for most commands)
        #await client.send_message(message.channel, "Ho ho ha ha!", tts=True)

    elif message.content.startswith('!sir'):
        # Yes, possibly having repeats is intentional, more fun that way
        placeOne = random.randint(1, (len(places) - 1))
        placeTwo = random.randint(1, (len(places) - 1))
        reply = "Sir, this is {}, not {}.".format(places[placeOne], places[placeTwo])
        await client.send_message(message.channel, reply)


# IMPROVEMENT give option to use args instead of cfg file
# if __name__ == "__main__":

user_config = open('user.cfg', 'r')
# TODO probably define a better cfg layout than username\n password
username = user_config.readline()
password = user_config.readline()
user_config.close()

username = username.strip('\n\r')
password = password.strip('\n\r')

client.run(username, password)

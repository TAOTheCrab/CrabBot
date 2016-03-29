#!/usr/bin/env python3
# Simple Discord chatbot for fun
#
# Requires user.cfg with valid username/password combo

import discord
import asyncio
import random
import logging

client = discord.Client()

mobas = ["Smite", "SMNC", "Strife", "Overwatch", "HoN", "AoS", "HotS"]

logging.basicConfig(level=logging.INFO)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.content.startswith('!takeover'):
        await client.send_message(message.channel, "Something something robots")

    if message.content.startswith('!dota') or message.content.startswith('!lol'):
        num = random.randint(1, (len(mobas) - 1))
        await client.send_message(message.channel, "This is a strange {} mod".format(mobas[num]))


# IMPROVEMENT give option to use args instead of cfg file
# if __name__ == "__main__":

user_config = open('user.cfg', 'r')
# TODO probably define a better cfg layout than username\n password
username = user_config.readline()
password = user_config.readline()
user_config.close()

client.run(username, password)

#!/usr/bin/env python3

import crabbot
import crabbotvoice # comment out to disable voice commands

import argparse
import asyncio
import logging
import readline  # Only for better terminal input support, eg. history
from threading import Thread

logging.basicConfig(level=logging.INFO)

# Do argparse first so that -h can print and exit before anything else happens
parser = argparse.ArgumentParser(description='A silly Discord bot')
token_args = parser.add_mutually_exclusive_group(required=True)
token_args.add_argument('-t', '--token',
                        help="The bot user's login token. Use this or -f.")
token_args.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help="A file with the bot user's login token as the first line. Use this or -t")

args = parser.parse_args()

if args.file is not None:
    login = args.file.readline().rstrip()
    args.file.close()
else:
    login = args.token


def poll_terminal():
    running = True
    # TODO function dict
    # TODO handle KeyboardInterrupt exception (cleans up console output)

    while running:
        term_input = input()
        if term_input == "help":
            # TODO print terminal command help
            print("Uh, no. I'm gonna be annoying instead.")
            # NOTES could use function.__doc__ and docstrings for function help
        elif term_input == "quit":
            # TODO figure out if it's possible to end discord.Client without KeyboardInterrupt
            #   Probably need to reimplement run() using start() with a different quit condition
            # Could also use run() and just throw a KeyboardInterrupt or two.
            # Ew...

            # For now, tell user how to quit so we don't leave them in the dark
            print("Disabling command input. Use ctrl+c to quit the bot.")
            running = False
        elif term_input.startswith("update_profile"):
            profile_args = term_input.split(' ')
            crabbot._update_profile(username=profile_args[1], avatar=profile_args[2])

input_thread = Thread(target=poll_terminal)
input_thread.start()

# Blocking, must be last. See discord.py Client for more info.
crabbot.bot.run(login)

input_thread.join()

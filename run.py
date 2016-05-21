#!/usr/bin/env python3

import crabbot
import crabbotmessages
import crabbotvoice  # comment out to disable voice commands entirely

import argparse
import asyncio
import logging
import readline  # Only for better terminal input support, eg. history
import sys
from threading import Thread

logging.basicConfig(level=logging.INFO)

# Do argparse first so that -h can print and exit before anything else happens
parser = argparse.ArgumentParser(description='A silly Discord bot')
token_args = parser.add_mutually_exclusive_group(required=True)
token_args.add_argument('-t', '--token',
                        help="The bot user's login token. Use this or -f.")
token_args.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help="A file with the bot user's login token as the first line. Use this or -t")
parser.add_argument('-p', '--prefix', default="!crab",
                    help="Command prefix the bot responds to")
parser.add_argument('--use-libav', action='store-true',
                    help="Voice uses Libav instead of FFmpeg")

args = parser.parse_args()

if args.file is not None:
    login = args.file.readline().rstrip()
    args.file.close()
else:
    login = args.token


bot = crabbot.CrabBot(prefix=args.prefix)


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
            bot._update_profile(username=profile_args[1], avatar=profile_args[2])
        elif term_input.startswith("disable_voice"):
            logging.info("Disabling voice commands")
            bot.remove_cog("Voice")
        elif term_input.startswith("enable_voice"):
            if "crabbotvoice" in sys.modules:
                logging.info("Enabling voice commands")
                bot.add_cog(crabbotvoice.Voice(bot, args.use_libav))
            else:
                logging.info("Voice disabled in source. Add/uncomment import for crabbotvoice and relaunch.")

input_thread = Thread(target=poll_terminal)
input_thread.start()

bot.add_cog(crabbotmessages.Messages(bot))
# Comment out import of voice to disable voice commands
if "crabbotvoice" in sys.modules:
    bot.add_cog(crabbotvoice.Voice(bot, args.use_libav))

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)

input_thread.join()

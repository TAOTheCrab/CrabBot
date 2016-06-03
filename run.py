#!/usr/bin/env python3

import argparse
import asyncio
import logging
import readline  # Only for better terminal input support, eg. history
import sys
from threading import Thread

import crabbot.common
import crabbot.messages
import crabbot.voice  # comment out to disable voice commands entirely


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
parser.add_argument('--assets-path', default="assets/",
                    help="Path for general assets (ex. sir-places.txt)")
parser.add_argument('--memes-path', default="assets/memes",
                    help="Path for memes audio clips (and its filelist.txt)")
parser.add_argument('--use-libav', action='store_true',
                    help="Make Voice use Libav instead of FFmpeg")
parser.add_argument('--disable-voice', action='store_true',
                    help="Disable Voice commands (can be enabled later)")

args = parser.parse_args()

if args.file is not None:
    login = args.file.readline().rstrip()
    args.file.close()
else:
    login = args.token


bot = crabbot.common.CrabBot(prefix=args.prefix)


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
            if "crabbot.voice" in sys.modules:
                logging.info("Enabling voice commands")
                bot.add_cog(crabbot.voice.Voice(bot, args.memes_path, args.use_libav))
            else:
                logging.info("Voice disabled in source. Add/uncomment import for crabbot.voice and relaunch.")
        elif term_input.startswith("update_lists"):
            bot.update_all_lists()

input_thread = Thread(target=poll_terminal)
input_thread.start()

bot.add_cog(crabbot.messages.Messages(bot, args.assets_path))
# Comment out import of voice to disable voice commands
if "crabbot.voice" in sys.modules and args.disable_voice is False:
    bot.add_cog(crabbot.voice.Voice(bot, args.memes_path, args.use_libav))

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)

input_thread.join()

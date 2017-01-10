#!/usr/bin/env python3
# Run script for CrabBot
# A mess of config args and terminal polling code
#
# See -h or read the argparse setup for argument details

import argparse
import datetime
import logging
import readline  # Only for better terminal input support, eg. history
import sys
from threading import Thread

import crabbot.common
import crabbot.cogs.messages
import crabbot.cogs.quotes
import crabbot.cogs.voice  # comment out to disable voice commands entirely


logging.basicConfig(filename='crabbot.log', level=logging.INFO)  # Grr, ytdl doesn't log
logging.info("Starting crabbot at " + str(datetime.datetime.now()))

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
parser.add_argument('--quotes-path', default="../",  # NOTE we write to this location, be careful where you put it
                    help="Path containing the quotes database (quotes.json. Do not include filename.)")
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
            # NOTE could use function.__doc__ and docstrings for function help
        elif term_input == "quit":
            # TODO figure out if it's possible to end discord.Client without KeyboardInterrupt
            #   Probably need to reimplement run() using start() with a different quit condition
            #   Could also use run() and just throw a KeyboardInterrupt or two.
            #   Ew...

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
            if "crabbot.cogs.voice" in sys.modules:
                logging.info("Enabling voice commands")
                bot.add_cog(crabbot.cogs.voice.Voice(bot, args.memes_path, args.use_libav))
            else:
                logging.info("Voice disabled in source. Add/uncomment import for crabbot.voice and relaunch.")
        elif term_input.startswith("update_lists"):
            bot.update_all_lists()

# Start polling thread as a daemon so the program exits without waiting if ex. the bot crashes
input_thread = Thread(target=poll_terminal, daemon=True)
input_thread.start()

bot.add_cog(crabbot.cogs.messages.Messages(bot, args.assets_path + "/messages"))
bot.add_cog(crabbot.cogs.quotes.Quotes(bot, args.quotes_path + "/quotes.json"))
# Comment out import of voice to disable voice commands
if "crabbot.cogs.voice" in sys.modules and args.disable_voice is False:
    bot.add_cog(crabbot.cogs.voice.Voice(bot, args.memes_path, args.use_libav))

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)

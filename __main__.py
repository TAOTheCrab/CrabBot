#!/usr/bin/env python3
# Run script for CrabBot
# A mess of config args and terminal polling code
#
# See -h or read the argparse setup for argument details

import argparse
import datetime
import logging
import os
import readline  # Only for better terminal input support, eg. history
import signal  # So we can send SIGINT to ourselves
import sys
from tempfile import gettempdir  # for PID file (for easier service management)
from threading import Thread

import crabbot.common
import crabbot.cogs.messages
import crabbot.cogs.quotes
import crabbot.cogs.voice  # comment out to disable voice commands entirely

pid = str(os.getpid())
pidfile = gettempdir() + '/CrabBot.pid'  # eg. so systemd's PIDFile can find a /tmp/CrabBot.pid
with open(pidfile, 'w') as temppidfile:
    temppidfile.write(pid)

logging.basicConfig(filename='crabbot.log', level=logging.INFO)  # Grr, ytdl doesn't log
logging.info("________\n" +
             "Starting CrabBot at " + str(datetime.datetime.now()) + "\n"
             "--------")  # Make it clear in the log when a new run starts
                          # TODO? Might want a delimiter that is easier to write, eg. for a log parsing script

# Do argparse first so that -h can print and exit before anything else happens
parser = argparse.ArgumentParser(fromfile_prefix_chars='@', description='A silly Discord bot')
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
                    help="Path containing the quotes database. Will create quotes.sqlite3 if it does not exist.")
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
    # TODO function dict instead of if/elif.

    while True:  # Run thread as daemon, so Python will exit despite this loop
        term_input = input()
        if term_input == "help":
            # TODO write help for the terminal commands
            print("Uh, no. I'm gonna be annoying instead.")
            # NOTE could use function.__doc__ and docstrings for function help
        elif term_input == "quit":
            os.kill(int(pid), signal.SIGINT)  # discord.Client.run() quits on KeyboardInterrupt, so...
            # This might not work on Windows? It has a special signal.CTRL_C_EVENT.
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
bot.add_cog(crabbot.cogs.quotes.Quotes(bot, args.quotes_path))
# Comment out import of voice to completely disable voice commands
if "crabbot.cogs.voice" in sys.modules and args.disable_voice is False:
    bot.add_cog(crabbot.cogs.voice.Voice(bot, args.memes_path, args.use_libav))

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)

# If it reaches here, CrabBot's probably logged out of Discord now
# (CrabBot doesn't log out if it's straight terminated)
logging.info("CrabBot has recieved a SIGINT and has now exited as intended\n" +
             "————— CrabBot exited at " + str(datetime.datetime.now()))
print("CrabBot says goodbye")

# Cleanup pidfile
try:
    os.remove(pidfile)
except:
    pass  # Don't try too hard to clean up

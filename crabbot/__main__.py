#!/usr/bin/env python3
# Run script for CrabBot
# A mess of config args and terminal polling code
#
# See -h or read the argparse setup for argument details

import argparse
import datetime
import logging
import os
from pathlib import Path
try:
    import readline  # Only for better terminal input support, eg. history. Does not work on Windows, but does work in WSL.
except ImportError:
    pass  # We don't use this import directly anyway
import signal  # So we can send SIGINT to ourselves
import sys
from tempfile import gettempdir  # for PID file (for easier service management)
from threading import Thread

import importlib.resources # Allows us to access assets from a package as a default
from contextlib import ExitStack # Needed to replicate pkg_resources usage in importlib

import crabbot.common
try:
    # This module has extra dependencies (youtube-dl), and is considered optional.
    # DISABLING UNTIL DISCORD.PY v2 MIGRATION IS COMPLETE
    #import crabbot.cogs.voice  # comment out to disable voice commands entirely
    pass
except ImportError as e:
    # Notify CLI, but otherwise don't block the run.
    print(f"Voice cog not loaded, missing dependency: {e.name}")

pid = str(os.getpid())
pidfile = Path(gettempdir() + '/CrabBot.pid')  # eg. so systemd's PIDFile can find a /tmp/CrabBot.pid
with open(pidfile, 'w') as temppidfile:
    temppidfile.write(pid)

# Load the default paths
pkg_resources_manager = ExitStack()
pkg_assets = importlib.resources.files(__name__) / 'assets'
pkg_memes = importlib.resources.files(__name__) / 'assets/memes'

# Do argparse first so that -h can print and exit before anything else happens
parser = argparse.ArgumentParser(fromfile_prefix_chars='@', description='A silly Discord bot')
token_args = parser.add_mutually_exclusive_group(required=True)
token_args.add_argument('-t', '--token',
                        help="The bot user's login token. Use this or -f.")
# BUG? I don't really know why this keeps throwing invalid token errors on my Windows machine (with Powershell 7), and debugging this is low priority right now
token_args.add_argument('-f', '--file', type=argparse.FileType('r'),
                        help="A file with the bot user's login token as the first line. Use this or -t")
parser.add_argument('-p', '--prefix', default="!crab",
                    help="Command prefix the bot responds to")
# The default is to grab the assets from its own distribution
parser.add_argument('--assets-path', type=Path, default=None, # None is used to determine if we need to load package resources
                    help="Path for general assets (ex. sir-places.txt)")
parser.add_argument('--memes-path', type=Path, default=None, # None is used to determine if we need to load package resources
                    help="Path for memes audio clips (and its filelist.txt)")
parser.add_argument('--quotes-path', type=Path, default=Path('.'),  # NOTE we write to this location, be careful where you put it
                    help="Path containing the quotes database. Will create quotes.sqlite3 if it does not exist.")
parser.add_argument('--use-libav', action='store_true',
                    help="Make Voice use Libav instead of FFmpeg")
parser.add_argument('--disable-voice', action='store_true',
                    help="Disable Voice commands (can be enabled later)")
parser.add_argument('-l', '--logfile', type=Path, default=Path('CrabBot.log'), 
                    help="Path, with filename, to write the log to")

args = parser.parse_args()

# BUG WINDOWS: If encoding is not specified as utf-8, logging tends to choke on newer emojis and not write anything.
# Waiting on change in Python 3.9 to add encoding arg to basicConfig.
#logging.basicConfig(filename=args.logfile, level=logging.INFO, encoding="utf-8")  # Grr, ytdl doesn't log
# In the meantime, create a working handler and continue
file_log = logging.FileHandler(args.logfile, encoding='utf-8')
logging.basicConfig(handlers=[file_log], level=logging.INFO,
                    format="{asctime}:{levelname}:{name}:{message}", style="{")

logging.info("________\n" +
             "Starting CrabBot at " + str(datetime.datetime.now()) + "\n"
             "--------")  # Make it clear in the log when a new run starts
                          # TODO? Might want a delimiter that is easier to write, eg. for a log parsing script

if args.file is not None:
    login = args.file.readline().rstrip()
    args.file.close()
else:
    login = args.token

if (args.assets_path is None):
    pkg_assets_path = pkg_resources_manager.enter_context(
        importlib.resources.as_file(pkg_assets)
    )
    args.assets_path = pkg_assets_path

# Initializing early so poll_terminal can refer to it. Otherwise it is kind of a poor grouping of control flow.
bot = crabbot.common.CrabBot(prefix=args.prefix, 
                             assets_path=args.assets_path,
                             quotes_path=args.quotes_path)


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
                bot.add_cog(crabbot.cogs.voice.Voice(bot.loop, args.memes_path, args.use_libav))
            else:
                logging.info("Voice disabled in source. Add/uncomment import for crabbot.voice and relaunch.")
        elif term_input.startswith("update_lists"):
            bot.update_all_lists()

# Start polling thread as a daemon so the program exits without waiting if ex. the bot crashes
input_thread = Thread(target=poll_terminal, daemon=True)
input_thread.start()

''' DISABLING TO FOCUS ON OTHER ASPECTS OF v2 MIGRATION. Need to add signaling to CrabBot to have it add the cog now that it has to be await-ed
# Example of adding a cog to CrabBot outside of CrabBot's init (...also voice is the iffiest module)
# Comment out import of voice to completely disable voice commands
if (args.memes_path is None):
    pkg_memes_path = pkg_resources_manager.enter_context(
        importlib.resources.as_file(pkg_memes)
    )
if "crabbot.cogs.voice" in sys.modules and args.disable_voice is False:
    bot.add_cog(crabbot.cogs.voice.Voice(bot.loop, args.memes_path, args.use_libav))
'''

# Blocking, must be last. See discord.py Client for more info.
bot.run(login)


# If it reaches here, CrabBot's probably logged out of Discord now
# (CrabBot doesn't log out if it's straight terminated)
logging.info("CrabBot has recieved a SIGINT and has now exited as intended\n" +
             "————— CrabBot exited at " + str(datetime.datetime.now()))
print("CrabBot says goodbye")

# Cleanup any importlib pkg files
pkg_resources_manager.close()

# Cleanup pidfile
try:
    os.remove(pidfile)
except:
    pass  # Don't try too hard to clean up

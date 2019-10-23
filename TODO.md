# Soon


# General
- [ ] Add logging (/exception handling mostly) for Quotes cog.
- [ ] Add print() for some logged messages for user feedback (mostly for eg. disable_voice command)

### Nice to have
- [ ] Might like to make a custom help formatter
    - see default discord.py commands.formatter.py and "formatter" commands.Bot arg
- [ ] setup.py
    - Needs a main script
    - Needs more testing
    - Probably needs additional metadata
    - Needs assets installed as extra data for setup()
        - crabbot.\_\_file\_\_ will give module path
    - use import+execfile script on a __main__.py?
- [ ] Data storage for persistent data (for ex. user permissions if those get implemented)
    - sqlite?
- [ ] Translation strings (mostly as an excuse to shorten the help= sections)
    - Idea: crabbot.load_help(), used by cogs to populate their help
    - Look into existing libraries for localization loading eg. managing translation txt files
        - gettext
            - tried, seems heavyweight for just populating text fields
    - Look into dynamic command aliases to translate them
- [ ] Module docstrings
- [ ] Function docstrings
- [ ] Add type hints to functions (see [typing](https://docs.python.org/3/library/typing.html))
    - Python 3.5 specific, so have to straight abandon pretense of 3.4 usability
    - Mostly just nice for keeping track of ex. which class is expected for function calls on args
        - (reading discord.py reminded me that duck typing is confusing with custom classes)
- [ ] Hidden !uptime command for CrabBot uptime
    - Candidate for admin check
- [ ] Admin permissions checks (not currently useful, but nice to have)
    - Bot manages its own permissions? (eg. internal list of allowed users)
    - Check for (configurable?) Discord server role?
        - alt. check user permissions (ex. Manage Server, Voice Move Member)
- [ ] Discord permissions link generator
    - Discord Developer Portal has a "permissions integer" generator on an app's Bot page in My Applications.
    - [Permissions docs](https://discordapp.com/developers/docs/topics/permissions)
        - Reminder: 0x1=b0001, 0x2=b0010, 0x4=b0100, 0x8=b1000
        - For link, convert to permissions hex/binary to int
    - [Add to server link docs](https://discordapp.com/developers/docs/topics/oauth2#adding-bots-to-guilds)


# run.py
- [ ] Some kind of status check command(s)
    - List contents of eg. the_memes (ex. check if --memes-path was correct without voice command)
- [ ] Better console (eg. not clobbered by log)
    - Could be solved with server/client for management
    - Currently worked around using iffy file logging (logs from youtube-dl leak)

### Nice to have
- [ ] Terminal command to change assets_path/memes_path live
    - Either remove then re-add related cog, or edit cog's path var and run update_lists()
- [ ] Server/client for commands?
    - Need some kind of shared key for auth
        - `--key` launch arg? Don't launch server without it?


# Voice
- [ ] catch discord.ext.commands.errors.CommandInvokeError for eg. invalid stream URLs
    - Disconnect from voice on error
        - (would like to do the error-prone task before connecting, but we're not there yet)
    - Note: YouTube-DL cannot validate URLs, so it can only throw errors in that case
- [ ] Might want to only let users in CrabBot's current voice channel use commands
- [ ] Reimplement volume commands

### Nice to have
- [ ] Command for info about current song (eg. a link)
    - Only really important when the stream message is either deleted or heavily buried
    - If possible, current playback time (eg. long stream you want timestamps for)
        - Might need either a per-song timer or a start time to calculate from
- [ ] Voice volume convert from ex. 100% to 1.0 notation
- [ ] Memes number selector
- [ ] Iterate over or choose from the contents of memes_path, instead of filelist.txt
    - Would make dynamic list easier, but maybe more abusable?
    - Could do ex. `Path.glob("*.dca")` and insist on a single file format
        - Multiple file formats would create too many hardcoded globs
            - Could instead try to use a library like [audioread](https://pypi.python.org/pypi/audioread)
                - Pydub?
        - Could do both, make a single (pre-encoded) format auto-detected, plus a manual filelist.txt
            - Pre-encoding is a bit annoying, so this is more user-friendly?
                - Alt. could make some kind of helper. Terminal command?
- [ ] Client.change_status() for stream
    - Set "game" name to stream title
    - Check if Game.url could be used for a link to the current source
- [ ] No-notify stream arg to disable @mention on playback
- [ ] Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - FFmpeg and Libav have libopus support

### Notes
- [x] Process voice audio before connecting to channel (reduce delay between joining and playing)
    - discord.py needs a voice connection before audio processing can start, so not possible
        - Obviously could break out of using discord.py to process audio


# Quotes

- [ ] Add command to remove a quote
    - Would be difficult with current data structure if quotes db gets too big
        - Could use some sort of quote id
- [ ] Quotes ID for easy reference, a la LRRBot?
- [ ] Per-server quotes
    - Would need:
        - Table initialization in "add" for a new server
        - General check in query functions
            - Notify user if no quotes have been added for the server


# Assorted notes (AKA thought this while busy with another thing)
- [ ] [cmd module](https://docs.python.org/3/library/cmd.html) for/instead of poll_terminal?
- [ ] Figure out multi-server stuff (currently untested, but might work as-is)
- [ ] Case-insensitive commands (not that important, just interesting)
    - Could override bot.on_message() and do str.lower() before bot.process_commands()
        - Problem: precludes commands having capitalizable args (eg. quotes)
            - Could copy process_commands' use of discord.ext.StringView.get_word to get the command
                - Doesn't work with subcommands
    - Probably requires adding a str.lower() in process_commands() when it's getting the "invoker"
- [ ] Some kind of live cog reload/reimport
    - Cogs are the most modified code, would be nice to not wait for re-login
    - importlib.reload()?
- [ ] Might have to move assets into crabbot for distribution
    - Alt. could somehow split out messages.py, since it's the thing that needs the assets badly
- [x] Rename run.py to __main__.py?
    - Allows automatic execution by calling the module name
    - for, ex., [zipapp](https://docs.python.org/3/library/zipapp.html)

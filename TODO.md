# Soon


# General
- [ ] Look into an exit more graceful than Interrupt
    - requires using client.start() instead of run()
- [ ] Full command logging
    - Logging.INFO level
    - Timestamp
    - Usage stats?
    - logging.Formatter() (see Python docs entry "Logging HOWTO")
    - Configurable logging to file
- [ ] Admin permissions checks (ex. for maxvolume command)
    - Bot manages its own permissions? (eg. internal list of allowed users)
    - Check for (configurable?) Discord server role?
        - alt. check user permissions (ex. Manage Server, Voice Move Member)
- [ ] Discord permissions link generator
    - [Permissions docs](https://discordapp.com/developers/docs/topics/permissions)
        - Reminder: 0x1=b0001, 0x2=b0010, 0x4=b0100, 0x8=b1000
        - For link, convert to permissions hex/binary to int
    - [Add to server link docs](https://discordapp.com/developers/docs/topics/oauth2#adding-bots-to-guilds)
- [ ] Need logging for exit/many other exceptions (see todo for clean exit)
- [ ] Add println for some logged messages for user feedback (mostly for eg. disable_voice command)
- [ ] Add logging for on_ready (currently only println)

### Nice to have
- [ ] Would like to make a custom help formatter
    - see default discord.py commands.formatter.py and "formatter" commands.Bot arg
- [ ] setup.py
- [ ] Data storage for persistent data (for ex. user permissions if those get implemented)
    - sqlite?
- [ ] Translation strings (mostly as an excuse to shorten the help= sections)
    - Idea: crabbot.load_help(), used by cogs to populate their help
    - Look into existing libraries for localization loading eg. managing translation txt files
- [ ] Module docstrings
- [ ] Function docstrings
- [ ] Add type hints to functions (see [typing](https://docs.python.org/3/library/typing.html))
    - Python 3.5 specific, so have to straight abandon pretense of 3.4 usability
    - Mostly just nice for keeping track of ex. which class is expected for function calls on args
        - (reading discord.py reminded me that duck typing is confusing with custom classes)


# run.py
- [ ] launch options in config file
    - Look into argparse's fromfile_prefix_chars
        - crabbot prefix? ex. crabbotargs.txt
- [ ] Some kind of status check command(s)
    - List contents of eg. the_memes (ex. check if --memes-path was correct without voice command)
- [ ] Better console (eg. not clobbered by log)
    - Could be solved with server/client for management
- [ ] Server/client for commands
    - Need some kind of shared key for auth
        - `--key` launch arg? Don't launch server without it?

### Nice to have
- [ ] Terminal command to change assets_path/memes_path live
    - Either remove then re-add related cog, or edit cog's path var and run update_lists()


# Voice
- [ ] Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - FFmpeg and Libav have libopus support
    - Make our own FFmpeg wrapper for StreamPlayer
        - youtube-dl --audio-format opus
        - Need Encoder class
            - encoder.frame_size
            - encoder.frame_length
        - Might be able to do these StreamPlayer args:
            - encoder=VoiceClientInstance.encoder
            - player=(lambda data:VoiceClientInstance.play_audio(data, encode=False))
    - Airhornbot's [load function](https://github.com/hammerandchisel/airhornbot/blob/master/cmd/bot/bot.go#L233):
        - Basically follows this part of the [spec](https://github.com/bwmarrin/dca/wiki/DCA1-specification#audio-data)
        - Reads the 16-bit signed little endian int header for the audio length in bytes
        - Uses that length to put the rest of the file into a bytes array
        - Simply appends the bytes array onto another bytes array as a buffer/queue
            - That buffer gets fed straight into an OpusSend of a Discord VoiceConnection
    - discord.py's opus.Encoder.encode() passes all audio through libopus's opus_encode
        - VoiceClient.play_audio(encode=False) skips encode()
            - For create_ffmpeg_player(), StreamPlayer(player=play_audio)
                - could do Streamplayer(player=(lambda data: play_audio(data, encode=False)))
- [ ] Command for info about current song (eg. a link)
    - Only really important when the stream message is either deleted or heavily buried
- [ ] Look over voice commands and put shared code in a function
    - eg. target_voice_channel check
- [ ] catch discord.ext.commands.errors.CommandInvokeError for eg. invalid stream URLs
    - Disconnect from voice on error
        - (would like to do the error-prone task before connecting, but we're not there yet)
- [ ] Livestreamer integration
    - Bonus alt YouTube streamer? (claims only Live tho)
        - Could hopefully start playing sooner than a full youtube-dl for longer videos
        - Would lose possibility of caching videos
    - At least look at [example code](http://docs.livestreamer.io/api_guide.html#simple-player) for audio buffer usage (they used GStreamer for ex.)
        - (... yes, CrabBot's audio handling is bad enough that it needs random buffer examples)
- [ ] Use "playing"/Discord.game for stream name/link?

### Nice to have
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

### Notes
- [x] Process voice audio before connecting to channel (reduce delay between joining and playing)
    - discord.py needs a voice connection before audio processing can start, so not possible
        - Obviously could break out of using discord.py to process audio
    - Probably solved by pre-encoding TODO (at least, would have do to our own processing)


# Assorted notes (AKA thought this while busy with another thing)
- [ ] cmd module for/instead of poll_terminal?
- [ ] Call loop.stop() to exit bot.run()?
    - discord.py does useful things in 'except KeyBoardInterrupt' though
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
- [ ] Use multiprocessing for Voice/individual voice connections?
    - Mostly just because a lot of Voice tasks hold up the main loop, and crash the bot
    - Make per-connection asyncio loop
    - Call bot loop with threadsafe(?)
    - Need/use concurrent.futures?

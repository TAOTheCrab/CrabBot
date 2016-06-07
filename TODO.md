# Soon

# Nice to have

## General
- [ ] Would like to make a custom help formatter
    - see default discord.py commands.formatter.py and "formatter" commands.Bot arg
- [ ] Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- [ ] Full command logging
    - Logging.INFO level
    - Timestamp
    - Usage stats?
    - logging.Formatter() (see Python docs entry "Logging HOWTO")
- [ ] user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location
    - Currently would only save passing -f or -t every launch, but we might want more options later
- [ ] Translation strings (mostly as an excuse to shorten the help= sections)
    - Idea: crabbot.load_help(), used by cogs to populate their help
    - Look into existing libraries for localization loading eg. managing translation txt files
- [ ] Admin permissions checks
    - ex. for maxvolume command
    - Check for (configurable?) role
        - alt. check user permissions (ex. Manage Server, Voice Move Member)
- [ ] setup.py
- [ ] Terminal command to change assets_path/memes_path
    - Probably would just have to remove then re-add related cog
- [ ] Add type hints to functions (see [typing](https://docs.python.org/3/library/typing.html))
    - Python 3.5 specific, so have to straight abandon pretense of 3.4 usability
    - Mostly just nice for keeping track of ex. which class is expected for function calls on args
        - (reading discord.py reminded me that duck typing is confusing with custom classes)
- [ ] Some kind of status check command(s)
    - List contents of eg. the_memes (ex. check if --memes-path was correct without voice command)

## Voice
- [ ] Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - Might be worth tweaking discord.py's calls to FFmpeg for places we can't bypass it entirely
        - FFmpeg and Libav have libopus support
        - Alternately, make our own FFmpeg wrapper for StreamPlayer
            - youtube-dl --audio-format opus
            - Need Encoder class
                - encoder.frame_size
                - encoder.frame_length
    - Airhornbot's [load function](https://github.com/hammerandchisel/airhornbot/blob/master/cmd/bot/bot.go#L233):
        - Basically follows this part of the [spec](https://github.com/bwmarrin/dca/wiki/DCA1-specification#audio-data)
        - Reads the 16-bit signed little endian int header for the audio length in bytes
        - Uses that length to put the rest of the file into a bytes array
        - Simply appends the bytes array onto another bytes array as a buffer/queue
            - That buffer gets fed straight into an OpusSend of a Discord VoiceConnection
    - discord.py's opus.Encoder.encode() passes all audio through libopus's opus_encode
        - VoiceClient.play_audio(encode=False) skips encode()
            - For ffmpeg_player, StreamPlayer(player=play_audio)
                - Streamplayer(player=(lambda data: play_audio(data, encode=False)))
- [ ] Voice volume convert from ex. 100% to 1.0 notation
- [x] Process voice audio before connecting to channel (reduce delay between joining and playing)
    - discord.py needs a voice connection before audio processing can start, so not possible
        - Obviously could break out of using discord.py to process audio
    - Probably solved by pre-encoding TODO (at least, would have do to our own processing)
- [x] Command line option to disable voice
    - Move import to conditional?
- [x] Check for youtube-dl module in stream command?
    - Mostly so the log can tell the user to pip install it instead of exception vomit
- [ ] Set up YoutubeDL cachedir
    - tempfile.TemporaryDirectory() for cross-platform?
- [ ] Iterate over or choose from the contents of memes_path, instead of filelist.txt
    - Would make dynamic list easier, but maybe more abusable?
    - Could do ex. `Path.glob("*.opus")` and insist on a single file format
        - Multiple file formats would create too many hardcoded globs
            - Could try to use a library like [audioread](https://pypi.python.org/pypi/audioread)
        - Could do both, make a single (pre-encoded) format auto-detected, plus a manual filelist.txt
            - Pre-encoding is a bit annoying, so this is more user-friendly?
                - Alt. could make some kind of helper. Terminal command?
- [ ] Command for info about current song (eg. a link)
    - Only really important when the stream message is either deleted or heavily buried
- [ ] Memes number selector

# Assorted notes (AKA thought this while busy with another thing)
- [ ] cmd module for/instead of poll_terminal?
- [ ] Call loop.stop() to exit bot.run()?
    - discord.py does useful things in 'except KeyBoardInterrupt' though
- [ ] Nice enhancement? (probably need if more than one Discord server): new subbot per server connection
    - Probably not the way to do this, just noting this to remind myself later
- [ ] Figure out if there's some, say, preprocessing we can do on voice audio to reduce slowdown
- [ ] Case-insensitive commands (not that important, just interesting)
- [ ] Put cogs in a "cogs" package? To make it clearer that they're modules instead of main code.

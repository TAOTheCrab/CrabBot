# Soon
- [ ] *after=end_playback* needs fixing. Currently gets called but does nothing.
    - Relook at discord.py playlist.py, was redone recently
        - It does call_soon_threadsafe, but only to signal an asyncio.Event() to stop waiting

# Nice to have

## General
- [ ] Would like to make a custom help formatter
    - see default discord.py commands.formatter.py and "formatter" commands.Bot arg
- [ ] Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- [ ] Command logging (probably Logging.INFO level. Timestamp. Usage stats?)
- [ ] user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location
    - Currently would only save passing -f or -t every launch, but we might want more options later
- [ ] Translation strings (mostly as an excuse to shorten the help= sections)
    - Idea: crabbot.load_help(), used by cogs to populate their help
    - Look into existing libraries for localization loading eg. managing translation txt files
- [ ] Admin permissions checks
    - ex. for maxvolume command
    - Check for (configurable?) role
        - alt. check user permissions (ex. Manage Server, Voice Move Member)
- [ ] crabbot.py just a class and/or library of shared state/functions
    - mostly done, needs a few checks/lookovers

## Voice
- [ ] Voice command queueing
- [ ] Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - Might be worth tweaking discord.py's calls to FFmpeg for places we can't bypass it entirely
        - FFmpeg has libopus support
        - Alternately, make our own FFmpeg wrapper for StreamPlayer
            - youtube-dl --audio-format opus
            - Need Encoder class (the whole idea is reducing the step of opus.encoder)
- [ ] Voice volume convert from ex. 100% to 1.0 notation
- [ ] Process voice audio before connecting to channel (reduce delay between joining and playing)

# Assorted notes (AKA thought this while busy with another thing)
- [ ] cmd module for/instead of poll_terminal?
- [ ] Give crabbotvoice its own asyncio thread/loop somehow?
    - stop_voice is notably delayed sometimes. player.stop() seems to work now, but bot lingers in channel
        - this causes a bug if it's awaiting a disconnect and someone calls an audio command during a long delay
    - Esp. with audio playing, responsiveness is important
- [ ] Call loop.stop() to exit bot.run()?
    - discord.py does useful things in 'except KeyBoardInterrupt' though
- [ ] Nice enhancement? (probably need if more than one Discord server): new subbot per server connection
    - Probably not the way to do this, just noting this to remind myself later
- [ ] Figure out if there's some, say, preprocessing we can do on voice audio to reduce slowdown
- [ ] Case-insensitive commands (not that important, just interesting)
- [ ] Make super-function for update_lists of various cogs
    - super-class?
    - register function, like the bot commands?

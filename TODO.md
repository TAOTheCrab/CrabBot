## Soon
- *after=end_playback* needs fixing. Currently gets called but does nothing.
    - Relook at discord.py playlist.py, was redone recently

## Nice to have
- Would like to make a custom help formatter
    - see default discord.py commands.formatter.py and "formatter" commands.Bot arg
- Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- Command logging (probably Logging.INFO level. Timestamp. Usage stats?)
- Voice command queueing
- user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location
    - Currently would only save passing -f or -t every launch, but we might want more options later
- Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - Might be worth tweaking discord.py's calls to FFMPEG for places we can't bypass it entirely
        - FFMPEG has libopus support
        - Alternately, make our own StreamPlayer
        - youtube-dl --audio-format opus
- Translation strings (mostly as an excuse to shorten the help= sections)
- Admin permissions checks
    - ex. for maxvolume command
    - Check for (configurable?) role
        - alt. check user permissions (ex. Manage Server, Voice Move Member)
- Voice volume convert from ex. 100% to 1.0 notation

## Look at later (AKA thought this while busy with another thing)
- cmd module for/instead of poll_terminal?
- wrap end_playback (and other functions called by threads) in call_soon_threadsafe()? Or create_task()? ensure_future()?
    - discord.Client has an explicit event loop we can call into at client_instance.loop
- Use @commands.command instead of using own decorator?
    - playlist.py seems to be using bot_instance.add_cog() to make this work
- Give crabbotvoice its own asyncio thread/loop somehow?
    - stop_voice is notably delayed sometimes. player.stop() seems to work now, but bot lingers in channel
        - this causes a bug if it's awaiting a disconnect and someone calls an audio command during a long delay
    - Esp. with audio playing, responsiveness is important
- Call loop.stop() to exit bot.run()?
    - discord.py does useful things in 'except KeyBoardInterrupt' though
- Nice enhancement? (probably need if more than one Discord server): new subbot per server connection
    - Probably not the way to do this, just noting this to remind myself later

## Fun

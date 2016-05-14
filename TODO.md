## Soon
- *after=end_playback* needs fixing. Currently gets called but does nothing.
    - Relook at discord.py playlist.py, was redone recently

## Backburner
- Convert voice section to handle its own voice client(s)
    - discord.py now handles multiple voice clients, so Bot.voice became voice_clients()
    - Nice enhancement? (probably need if more than one server): new subbot per server connection
        - Probably not the way to do this, just noting this to remind myself later

## Nice to have
- Would like to make a custom help formatter
(see default [formatter](https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/formatter.py)
and "formatter" commands.Bot arg)
- Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- Command logging (probably Logging.INFO level. Timestamp. Usage stats?)
- Voice command queueing
- Volume control (eg. '-af "volume={}"'.format{x}) Be sure to clamp (might make 20%/0.2 the max to not take over channels)
- user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location
    - Currently would only save passing -f or -t every launch, but we might want more options later
- Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - Might be worth tweaking discord.py's calls to FFMPEG for places we can't bypass it entirely
        - FFMPEG has libopus support
        - Alternately, make our own StreamPlayer
        - youtube-dl --audio-format opus
- Translation strings (mostly as an excuse to shorten the help= sections)

## Look at later (AKA thought this while busy with another thing)
- cmd module for/instead of poll_terminal?
- wrap stop_voice (and other functions called by threads) in call_soon_threadsafe()? Or create_task()? ensure_future()?
    - discord.Client has an explicit event loop we can call into at client_instance.loop
- Use @commands.command instead of using own decorator?
    - playlist.py seems to be using bot_instance.add_cog() to make this work

## Fun

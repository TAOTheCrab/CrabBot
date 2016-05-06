## Soon

## Nice to have
- Would like to make a custom help formatter
(see default [formatter](https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/formatter.py)
and "formatter" commands.Bot arg)
- Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- Split into modules (eg. running the bot, voice, management?, grouped commands? cogs?)
- Command logging (probably Logging.INFO level. Timestamp. Usage stats?)
- Voice command queueing
- Volume control (eg. '-af "volume={}"'.format{x}) Be sure to clamp (might make 20%/0.2 the max to not take over channels)
- user.cfg. Look into argparse's fromfile_prefix_chars, otherwise have default location and arg-defined location
    - Currently would only save passing -f or -t every launch, but we might want more options later
- Voice pre-encoded for opus (see AirhornBot's use of DCA)
    - Might be worth tweaking discord.py's calls to FFMPEG for places we can't bypass it entirely
        - FFMPEG has libopus support
- Translation strings (mostly as an excuse to shorten the help= sections)

## Fun

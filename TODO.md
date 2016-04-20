Soon
- Voice output tends to cut out after a certain time, as if ffmpeg gets suspended. Investigate. Might be computer-specific.
    - Might be gone now? Test
- Put eg. places into a better storage space. Plain files? sqlite?
    - a db would be nice for edited-while-running word lists. A little overblown though.
    - in-memory list to plain text. Have to figure out command line text input and safe shutdown.

Nice to have
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

Fun

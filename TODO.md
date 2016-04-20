In progress (late night brainstorm so I don't forget)
- Words data structure
    - Integrate random.choice()?
    - Do we have to use getters/setters to ensure async is referring to a global shared resource?
        - Probably will work the same as before with global lists...
    - The problem is that async functions seem to have their own space
        - So an async update_vars may be creating its own eg. mobas var and thus deleting it when it's done

Soon
- Need solution for handling voice player state (with bot.command decorator, might be difficult to eg. make a class)
- Voice output tends to cut out after a certain time, as if ffmpeg gets suspended. Investigate. Might be computer-specific.
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
- Voice command queueing (need voice system to be responsive first...)

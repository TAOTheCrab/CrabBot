Soon
- Need solution for handling voice player state (with bot.command decorator, might be difficult to eg. make a class)
- Put eg. places into a better storage space. Plain files? sqlite? (a db would be nice for edited-while-running word lists. A little overblown though.)

Nice to have
- Would like to make a custom help formatter
(see default [formatter](https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/formatter.py)
and "formatter" commands.Bot arg)
- Look into an exit more graceful than Interrupt (requires using client.start() instead of run())
- Split into modules (eg. voice, management?, grouped commands? cogs?)
- Command logging (probably Logging.INFO level. Timestamp. Usage stats?)

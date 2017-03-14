CrabBot
=======

Silly Discord bot for funsies

Mostly prints funny messages in reply to commands, with some additional voice functionality

**This should be considered alpha-quality software.** There are some
glaring bugs, missing features, and most of it is undocumented

**Do not use the setup.py, it is WIP**

By default, use !crabhelp or "@\*botname\* help" to see a list of visible commands

Requires:

- `discord.py <https://github.com/Rapptz/discord.py>`__ v0.10+ (AKA async branch)
    - ``pip3 install discord.py[voice]`` for voice support
- Python 3.5+ (uses async syntax, can be edited to work with 3.4)

For voice (module can be disabled):

- libopus0/opus (for voice transmission. Package name depends on package manager)
- ffmpeg (for voice file playback)
    - Voice module can be configured to use avconv/libav instead (eg. for Debian)
- youtube-dl (for stream command)

Needs a bot user token. See ``-h`` for details

Common usage is

``python3 __main__.py -f FileWithUserTokenAsFirstLine``

or

``python3 __main__.py -t UserToken``

You can also make a text file with common arguments and refer to it with
the arg "@\*filename\*", which you can mix with regular args

For instance, for a custom prefix with custom assets, use a file like
this::

    -p
    !banana
    --assets-path
    ./banana-messages

Then launch CrabBot with:

``python3 __main__.py -f TokenFile @bananas.txt``


Similar projects
----------------

- `Red <https://github.com/Twentysix26/Red-DiscordBot>`__ - Another
discord.py bot, similarly uses cogs for most commands

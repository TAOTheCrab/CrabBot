CrabBot
=======

**NOTE: This library-rewrite-prep branch uses the version of Discord.py from the `rewrite/1.0 branch <https://github.com/Rapptz/discord.py/tree/rewrite>`__ **

Silly Discord bot for funsies

Mostly prints funny messages in reply to commands, with some additional voice functionality

**This should be considered alpha-quality software.** There are some
glaring bugs, missing features, and most of it is undocumented

**Do not use the setup.py, it is WIP**

By default, use !crabhelp or "@\*botname\* help" to see a list of visible commands

Requires:

- `discord.py <https://github.com/Rapptz/discord.py>`__ v1.0+ (AKA **rewrite** branch)

  - ``pip3 install discord.py[voice]`` for voice support
    
    - **TEMP UNTIL PYPI RELEASE OF REWRITE BRANCH** ``pip3 install git+https://github.com/Rapptz/discord.py.git@rewrite#egg=discord.py[voice]``


- Python 3.6+ (uses `f-strings <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`__, can be edited for 3.5)

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

CrabBot
=======

NOTE: I haven't been actively running this lately due to losing its dedicated server, so I'm not sure what's broken by Discord changes. Please file an issue if needed.

Silly Discord bot for funsies

Mostly prints funny messages in reply to commands, with some additional voice functionality

**This should be considered alpha-quality software.** There are some
glaring bugs, missing features, and most of it is undocumented

This bot's primary dev/working environment is Linux / MSYS2. 
Native Windows compatibility is not guaranteed, 
but is occassionally tested and fixed up as a curiosity.
(ex. issues with the difference in preferred file encoding, only lightly tested as fixed)

**Please report any issues with running as an installed package. Recommended method is still running from source, though basic testing of `poetry build` + `pip` showed no issues.**

Quickstart using `Poetry <https://python-poetry.org>`__: 

- ``poetry install``
- ``poetry run python -m crabbot -f FileWithUserTokenAsFirstLine``

By default, use !crabhelp or "@\*botname\* help" to see a list of visible commands

Requires:

- `discord.py <https://github.com/Rapptz/discord.py>`__ v2.0+

- Python 3.8+

~~For voice~~ CURRENTLY DISABLED - Not converted to discord.py v2 yet (module will automatically be disabled if dependencies are missing):

- ``discord.py[voice]``
- ``youtube-dl`` (for stream command)
- Native packages

  - ``opus`` / ``libopus0`` (for voice transmission)
  - ``ffmpeg`` (for voice file playback)

    - Can be configured to use ``avconv`` / ``libav`` instead (eg. for Debian)

Needs a bot user token. See ``-h`` for details

Common usage is

``python3 -m crabbot -f FileWithUserTokenAsFirstLine``

or

``python3 -m crabbot -t UserToken``

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

- `Red <https://github.com/Twentysix26/Red-DiscordBot>`__ - 
  Another discord.py bot, similarly uses cogs for most commands

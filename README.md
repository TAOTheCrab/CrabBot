# CrabBot
Silly Discord bot for funsies

Mostly prints funny messages in reply to commands, with some additional voice functionality

**This should be considered alpha-quality software.**
There are some glaring bugs, missing features, and most of it is undocumented.  

By default, use !crabhelp or "@*botname* help" to see a list of visible commands

Requires:
- [discord.py](https://github.com/Rapptz/discord.py) v0.10 (async beta)
- Python 3.5+ (uses async syntax, can be edited to work with 3.4)

For voice (can be disabled, or errors safely ignored):
- libopus0 *or* opus (for voice transmission. Package name depends on package manager)
- ffmpeg (for voice file playback)
    - Voice module can be configured to use avconv/libav instead (eg. for Debian)
- youtube-dl (for stream command)

Needs a bot user token. See -h for details.

Common usage is

`python3 run.py -f FileWithUserTokenAsFirstLine`

or

`python3 run.py -t UserToken`

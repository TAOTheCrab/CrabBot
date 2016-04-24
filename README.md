# CrabBot
Silly Discord bot for giggles and testing

Mostly prints funny messages in reply to commands

By default, use !crabhelp or "@-*botname*- help" to see a list of visible commands

Requires:
- [discord.py](https://github.com/Rapptz/discord.py) v0.10 (async beta)
- Python 3.5+ (uses async syntax, can be edited to work with 3.4)

For voice (voice commands will throw errors if not installed, but other commands should still work):
- libopus / opus (for voice transmission)
- ffmpeg (for voice file playback. provided test sound requires libvorbis support.)

Needs a bot user token. See -h for details.

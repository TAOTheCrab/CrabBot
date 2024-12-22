# INSTRUCTIONS WIP

NOTE: Anything in `< >` is a placeholder that you will have to replace with values appropriate for your setup

## Quick dev setup

```bash
cd <CrabBotDir>

# Optional, mostly for distros where a native package is available but not a prebuilt PyPI wheel (eg. Msys2, ARM distros)
# (may need to run `poetry lock` to ensure it doesn't try to install outdated versions overtop)
python -m venv --system-site-packages .venv

poetry install

# Run CrabBot
# Note that CrabBot will create files in $PWD by default, so ideally this would be run from a separate folder
./.venv/bin/python -m crabbot <token file method>
```

## Notes

GNU screen is handy for remote work. Run CrabBot in `screen -S CrabBotRun`, then `ctrl+a d`. `screen -R` to reattach.

For voice, the `opus`/`libopus0` package may need to be installed separately (I forget what happens, but the issue might only appear at runtime)

For Msys2 or any other distro having trouble with native Python dependencies, the following distro packages may be useful to grab and make available as system packages in your venv (basically any package that poetry fails or is too slow to compile):

```bash
pacman -S python-aiohttp
# Optional, for voice
pacman -S python-pynacl 
```

## start-crabbot.sh

```bash
#!/bin/bash

# New files will be created in the working dir, be careful
CRABBOTWORKDIR=<path to working dir>
CRABBOTENV=<path to venv>
CRABBOTARGS="<either file or token args> <additional args, ex. --memes-path*>"

cd $CRABBOTWORKDIR

# Create a new detached screen
screen -d -m -S CrabBotRun $CRABBOTVENV/bin/python -m crabbot $CRABBOTARGS
echo "Use \`screen -R CrabBotRun\` to control CrabBot"

```

## crabbot.service (for systemd)

Some help from [Red's docs](https://twentysix26.github.io/Red-Docs/red_guide_linux_autostart/)

Put in `/etc/systemd/system`

```ini
[Unit]
Description=Start CrabBot at startup.
After=network-online.target

[Service]
Type=forking
PIDFile=/tmp/CrabBot.pid
User=<USERNAME>
# Alternately you can just copy the executing line here instead of the shell script: 
# `screen -d -m -S CrabBotRun <CRABBOTVENV>/bin/python -m crabbot <CRABBOTARGS>`
ExecStart=<CrabBotDir>/start-crabbot.sh
KillSignal=SIGINT
WorkingDirectory=<CrabBotDir>
# Restart=always

[Install]
WantedBy=multi-user.target
```

Notes: [NetworkTarget](https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/)

Then `systemctl enable crabbot.service` and `systemctl start crabbot.service`

Reference: [Autostart Process Gnu Screen Systemd](http://www.linuxveda.com/2014/04/28/autostart-process-gnu-screen-systemd/)

## Read the log file live

`tail -f crabbot.log`

## (OLD, kept mostly for package list) Debian Jesse (ex. Raspberry Pi Raspian)

```bash
apt install libffi-dev libreadline-dev libssl-dev libopus0

# Install or compile an updated Python >=3.8

# Install Python module dependencies
pip3 install discord.py[voice]
pip3 install yt-dlp

git clone <CrabBot git>
cd CrabBot
python3 __main__.py <whichever token method> --use-libav
```

Rasbian alternately has ffmpeg (instead of libav) in jesse-backports

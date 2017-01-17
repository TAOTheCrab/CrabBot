# INSTRUCTIONS WIP

# Debian Jesse (ex. Raspberry Pi Raspian)
```
apt install libffi-dev libreadline-dev libssl-dev libopus0

# Compile Python 3.5 if it doesn't exist as a package
wget *python 3.5+*
tar xzf *python*.tgz
cd *python*
./configure (--prefix=*blah*)
make -j(*numCPUs*)
make install
cd ..

# (optional) Set up virtual env
(*blah*/)pyvenv ./CrabBotEnv
cd CrabBotEnv
source bin/activate

# Install Python module dependencies
pip3 install discord.py[voice]
pip3 install youtube-dl

git clone *CrabBot git*
cd CrabBot
python3 __main__.py (whichever token method) --use-libav
```

Rasbian alternately has ffmpeg (instead of libav) in jesse-backports

GNU screen is handy for remote work. Run CrabBot in `screen -S CrabBotRun`, then `ctrl+a d`. `screen -R` to reattach.

# Extra Linux/Mac stuff

Use `pyvenv` to create virtual environments

## start-crabbot.sh

```
#!/bin/bash

CRABBOTENV=*CrabBotVEnvDir*
CRABBOTARGS="*either file or token args* *additional args, ex. --memes-path*"

cd $CRABBOTENV
source bin/activate  # Can remove this if not using a virtual env
cd CrabBot  # Can also remove this if not using a virtual env

# Create a new detached screen
screen -d -m -S CrabBotRun python3 __main__.py $CRABBOTARGS
echo "Use \`screen -R CrabBotRun\` to control CrabBot"

```

## crabbot.service (for systemd)

Some help from [Red's docs](https://twentysix26.github.io/Red-Docs/red_guide_linux_autostart/)

Put in `/etc/systemd/system`

```
[Unit]
Description=Start CrabBot at startup.
After=network-online.target  # might be too early?

[Service]
Type=forking
User=*USERNAME*
ExecStart=*CrabBotDir*/start-crabbot.sh
ExecStop=screen -X -S CrabBotRun quit  # KillSignal=SIGINT instead? Phantom login bug currently
WorkingDirectory=*CrabBotDir*
# Restart=always

[Install]
WantedBy=multi-user.target
```

Notes: [NetworkTarget](https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/)

Then `systemctl enable crabbot.service` and `systemctl start crabbot.service`

Reference: [Autostart Process Gnu Screen Systemd](http://www.linuxveda.com/2014/04/28/autostart-process-gnu-screen-systemd/)

## Read the log file live

`tail -f crabbot.log`

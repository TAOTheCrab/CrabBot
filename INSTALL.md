# INSTRUCTIONS WIP

# Debian Jesse (ex. Raspberry Pi Raspian)
```
apt-get install libffi-dev libreadline-dev libssl-dev libopus0

# Compile Python 3.5
wget *python 3.5+*
tar xzf *python*.tgz
cd *python*
./configure (--prefix=*blah*)
make -j(*numCPUs*)
make install

# Set up virtual env
cd ..
(*blah*/)pyvenv ./CrabBotEnv
cd CrabBotEnv
source bin/activate
pip3 install *discord.py git async branch*
pip3 install youtube-dl
git clone *CrabBot git*
cd CrabBot
python3 run.py (whichever token method) --use-libav
```

Rasbian alternately has ffmpeg in jesse-backports

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
screen -d -m -S CrabBotRun python3 run.py $CRABBOTARGS
echo "Use \`screen -R CrabBotRun\` to control CrabBot"

```

## crabbot.service (for systemd)

```
[Unit]
Description=Start CrabBot at startup.

[Service]
Type=forking
User=*USERNAME*
ExecStart=*CrabBotDir*/start-crabbot.sh
ExecStop=screen -X -S CrabBotRun quit
WorkingDirectory=*CrabBotDir*

[Install]
WantedBy=multi-user.target
```

Then `systemctl enable crabbot.service` and `systemctl start crabbot.service`

Reference: [Autostart Process Gnu Screen Systemd/](http://www.linuxveda.com/2014/04/28/autostart-process-gnu-screen-systemd/)

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

GNU screen is handy for remote work. Run CrabBot in `screen -S CrabBotRun`, then `ctrl+a d`. `screen -R` to reattach.

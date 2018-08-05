# BlockerBot

Minimalistic bot designed to help server owners fight spam in form of users joining with invites as usernames. 

Commands:

`!!help`: Shows bot info

`!!alive`: Checks if the bot is alive

`!!output channel`: Set the logging output

`!!exit`: ADMINS ONLY; Kills the bot


----

# Setup

You need [Python 3](https://www.python.org/). 

You'll also need a token and a client ID for the Discord. Set up an app at https://discordapp.com/developers/applications/me
**Both need to be Strings!** (if you don't know how to define Strings, it's as easy as replacing `None` with `""`, and writing your token/ID between the quotes. I.e. `"abcd1234"`). Add them to the `Bot.py` file; the variables are pre-defined. Then run `pip install discord`. You may need to run `pip3 install discord`. 

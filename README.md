# autokick
Custom bot that kicks users who fail to verify after a set period of time. 

You'll need discord.py, obviously. Also fill in the info in config.json with the following details:

* `key`: Your bot's token.
* `server`: The server you wish to run the bot in.
* `role`: The role your autorole gives to users who aren't verified.
* `channel`: A channel where unverified users are allowed to send messages.
* `log`: A channel where kick messages are sent.
* `notif`: A channel where young account warnings are sent. This can be the same as the log channel.

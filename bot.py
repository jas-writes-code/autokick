from discord import *
import re
import time
import json

client = Client(intents=Intents.all())
with open('config.json', 'r') as file:
    config = json.load(file)
key = config["cfg"]["key"]
server = config["cfg"]["server"]
role = config["cfg"]["role"]
channel = config["cfg"]["channel"]
logChannel = config["cfg"]["log"]
notif = config["cfg"]["notif"]
cooldown = 2500
reminder = f"Welcome <@&{role}>! This is your periodic reminder to follow the instructions in <#876517050925846638> to see the rest of the server! If you fail to do so within 48 hours of joining, you will be kicked.\n*I'm a bot. Beep boop.*"

@client.event
async def on_ready():
    global log, waiting, server
    log = client.get_channel(int(logChannel))
    waiting = client.get_channel(int(channel))
    notif = client.get_channel(int(notif))
    server = client.get_guild(int(server))
    print('-----')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    print("The bot works -- this terminal will not provide further feedback unless there is an error. It's safe to detach this window.")

async def checkMessages(user):
    for identifier, data in config["messages"].items():
        if int(identifier) == user.id:
            return data["time"]
    return None

async def updateList(kick):
    await log.send("Checking member list. Members with Unverified role, who joined more than 48 hours ago, and have not sent a message in 24 hours, will be kicked.")
    total = 0
    for member in server.members:
        for element in member.roles:
            if element.id == int(role):
                latest = await checkMessages(member)
                join = member.joined_at.timestamp()
                if latest is not None and kick:
                    total += 1
                    allowance = max(latest + 172800 / 2, join + 172800)
                    if allowance < time.time():
                        await server.kick(member)
                        await log.send(f'User <@{member.id}> was kicked as they failed to verify in time! <@{member.id}> joined <t:{int(join)}:R> and their last tracked message was <t:{latest}:R>.')
                    elif join + 172800 < time.time():
                        await server.kick(member)
                        await log.send(f'User <@{member.id}> was kicked as they failed to verify in time! <@{member.id}> joined <t:{int(join)}:R> and has no tracked messages.')
                elif latest and not kick:
                    allowance = max(latest + 172800 / 2, join + 172800)
                    if allowance < time.time():
                        await log.send(f'User <@{member.id}> has been a member for **{int(int(time.time() - join) / 60 / 60)}** hours, their last tracked message was **{int(int(time.time() - latest) / 60 / 60)}** hours ago, and has failed to verify! No action was taken, as kicking is disabled in bot.py.')
                elif join + 172800 < time.time():
                    await log.send(f'User <@{member.id}> has been a member for **{int(int(time.time() - join) / 60 / 60)}** hours, has no tracked messages, and has failed to verify! No action was taken, as kicking is disabled in bot.py.')
    await log.send(f"Check complete!")
    if kick:
        if ping is not None:
            ping.delete()
        await waiting.send(f'**{total}** users were just kicked as they failed to verify in time!')
        ping = await waiting.send(reminder)

@client.event
async def on_message(message):
    global cooldown
    if message.guild.id == server.id and message.author.id != 892286562606383156:
        cooldown += 1
        member = message.author
        if message.author.joined_at is not None:
            for element in member.roles:
                if element.id == int(role):
                    new_entry = {
                        "message": message.id,
                        "time": int(time.time())
                    }
                    id = message.author.id
                    config["messages"][id] = new_entry
                    with open('config.json', 'w') as file:
                        json.dump(config, file, indent=4)
                    break
        if cooldown > 1000:
            cooldown = 0
            await updateList(False) # set this to False if you don't want to kick people

@client.event
async def on_member_join(member):
    if member.guild.id == server.id:
        join = member.joined_at.timestamp()
        create = member.created_at.timestamp()
        overlap = (join - create) / 60
        if overlap < 60:
            await notif.send(f"<@{member.id}> joined on a fresh account.\nUnderlap: **{int(overlap)}** minute(s)\nCreated <t:{int(create)}:f>.")
        elif overlap < 1440:
            await notif.send(f"<@{member.id}> joined on a fresh account.\nUnderlap: **{int(overlap / 60)}** hour(s) \nCreated <t:{int(create)}:f>.")

@client.event
async def on_member_leave(member):
    if member.guild == server:
        if member.id in config["messages"]:
            del config["messages"][member.id]
            with open('config.json', 'w') as file:
                json.dump(config, file, indent=4)

@client.event
async def on_member_update(before, after):
    if before.guild == server:
        if before.roles != after.roles:
            id = discord.Object(id=role)
            if id not in after.roles:
                if str(role) in config["messages"]:
                    del config["messages"][after.id]
                    with open('config.json', 'w') as file:
                        json.dump(config, file, indent=4)

client.run(str(key))

from discord import *
import re
import time
import json

client = Client(intents=Intents.all())
with open('config.json', 'r') as file:
    config = json.load(file)
key = config["cfg"]["key"]
server = int(config["cfg"]["server"])
role = config["cfg"]["role"]
channel = config["cfg"]["channel"]
logChannel = int(config["cfg"]["log"])
log = client.get_channel(int(logChannel))
kicklist = []
cooldown = 0
reminder = f"Welcome <@&{role}>! This is your periodic reminder to follow the instructions in <#1189684060075855932> to see the rest of the server! If you fail to do so within 48 hours of joining, you will be kicked. \n \n *I am a bot, and this action was performed automatically. Beep Boop.*"

@client.event
async def on_ready():
    print('-----')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('-----')
    print("The bot works -- this terminal will not provide further feedback unless there is an error. It's safe to detatch this window.")

async def checkMessages(user):
    for element in config["messages"]:
        if element == user.id:
            return element[1]
        else:
            return

async def updateList(message):
    await message.channel.send("Checking member list. Members with Unverified role, who joined more than 48 hours ago, and have not sent a message in 24 hours, will be kicked.")
    for member in message.guild.members:
        for element in member.roles:
            if element.id == int(role):
                latest = await checkMessages(member)
                join = member.joined_at.timestamp()
                if latest is not None:
                    allowance = max(latest + 172800 / 2, join + 172800)
                    if allowance < time.time():
                        await member.guild.kick(member)
                        await message.channel.send(f'User <@{member.id}> was kicked as they failed to verify in time! <@{member.id}> joined <t:{int(member.joined_at.timestamp())}:R> and their latest message was <t:{latest}:R>.')
                elif join + 172800 < time.time():
                    await member.guild.kick(member)
                    await message.channel.send(f'User <@{member.id}> was kicked as they failed to verify in time! <@{member.id}> joined <t:{int(member.joined_at.timestamp())}:R> and has no tracked messages.')
    await message.channel.send(f"Check complete!\n{reminder}")

@client.event
async def on_message(message):
    for element in message.author.roles:
        if element.id == int(role):
            if message.channel == int(channel):
                new_entry = {
                    "message": message.id,
                    "time": time.time()
                }
                id = message.author.id
                config["messages"][id] = new_entry
                with open('scores.json', 'w') as file:
                    json.dump(config, file)
#                cooldown += 1
    if cooldown >= 50:
        await updateList(message)

@client.event
async def on_member_join(member):
    join = member.joined_at.timestamp()
    create = member.created_at.timestamp()
    overlap = (join - create) / 60
    if overlap < 60:
        await log.send(f"<@{member.id}> joined on a fresh account.\nUnderlap: {int(overlap)} minute(s)\nCreated <t:{create}:f>.")
    elif overlap < 1440:
        await log.send(f" <@{member.id}> joined on a fresh account.\nUnderlap: {int(overlap / 60)} hour(s) \nCreated <t:{create}:f>.")

client.run(str(key))

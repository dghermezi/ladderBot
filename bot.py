import discord
from discord.ext.commands import Bot
from discord.ext import commands
import logging
import json
import os.path
import trueskill

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = Bot(command_prefix="!")

#users = {}
#users['Videowaffles'] = {
#    'id': 1,
#    'points': 100
#}
#users['Kay'] = {
#    'id': 2,
#    'points': 100
#}
#s = json.dumps(users)

#with open("users.json", "w") as f:
#    f.write(s)


@bot.event
async def on_read():
    print("Client logged in")

@bot.command()
async def hello(message):
    msg = 'Hello {0.author.mention}'.format(message)
    await client.send_message(message.channel, msg)

@bot.command(pass_context=True)
async def register(ctx):
    #await bot.say("Registering/checking if you're already registered. please give me a sec!")

    if os.path.isfile("users.json") == False:
        users = {}
        users[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "points": 500,
        "matched": 0
        }
        f = open("users.json", "w+")
        s = json.dumps(users)
        with open ("users.json", "w+") as f:
            f.write(s)
        f.close()
        return await bot.say(ctx.message.author.name + " is now registered!")

    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if ctx.message.author.id in users:
            return await bot.say("You're already registered!")
        else:
            users[ctx.message.author.id] = {
                    "name": ctx.message.author.name,
                    "points": 500,
                    "matched": 0
                    }
            f = open("users.json" ,"w")
            s = json.dumps(users)
            with open("users.json", "w") as f:
                f.write(s)
            f.close()
            return await bot.say(ctx.message.author.name + " is now registered!")

@bot.command()
async def points(member : discord.Member):
    if os.path.isfile("users.json") == False:
        return
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if member.id in users:
            return await bot.say(member.name + " has " + str(users[member.id]["points"]) + " points!")
        else:
            return await bot.say(member.name + " is not registered!")
        #for user in users:
        #    found = 0
        #    if users[user]["id"] == str(member.id):
        #        found = 1
        #        return await bot.say(member.name + " has " + str(users[user]["points"]) + " points!")
        #if found == 0:
        #    return await bot.say(member.name + " is not registered!")

@bot.command(pass_context=True)
async def challenge(ctx, member : discord.Member):
    if os.path.isfile("users.json") == False:
        return await bot.say("neither of you are registered!")
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if (ctx.message.author.id in users) == False:
            return await bot.say("You're not registered")
        if (member.id in users) == False:
            return await bot.say(member.name + " is not registered!")
        else:
            await bot.say(ctx.message.content)
            return await bot.say("you're both registered")

bot.run("Mjk3MTA2MjcwMDc3NTgzNDAx.C78Vqg.7mwzkkPmwP1MxFJ1Oqr51AxPpjg")

# Author: David G. (Videowaffles)
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import logging
import json
import os.path
import trueskill

#things left to implement
#
#assign trueskill to everyone
#leaderboards
#change points to trueskill points
#make it so you cant challenge/be challenged/accept a match if youre currently in one
#cancel matches without forfeit? up to tempo i guess
#find a way to save trueskill


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
        return await bot.say(member.name + " is not registered!")
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

#todo: let someone challenge more than one person at a time
@bot.command(pass_context=True)
async def challenge(ctx, member : discord.Member):
    if ctx.message.author.id == member.id:
        return await bot.say("You can't challenge yourself!")
    if os.path.isfile("users.json") == False:
        return await bot.say("You're not registered!")
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if (ctx.message.author.id in users) == False:
            return await bot.say("You're not registered!")
        if (member.id in users) == False:
            return await bot.say(member.name + " is not registered!")
        else:
            if os.path.isfile("challenges.json") == False:
                f = open("challenges.json", "w+")
                challenges = {}
                challenges[ctx.message.author.id] = {
                "p1name": ctx.message.author.name,
                "p2id": member.id,
                "p2name": member.name,
                "p1report": 0,
                "p2report": 0,
                "p2accept": 0
                }
                s = json.dumps(challenges)
                with open ("challenges.json", "w+") as f:
                    f.write(s)
                f.close()
            else:
                f = open("challenges.json", "r")
                s = f.read()
                challenges = json.loads(s)
                if (ctx.message.author.id in challenges):
                    if challenges[ctx.message.author.id]["p2accept"] == 1:
                        await bot.say(ctx.message.author.mention + ", you already have an accepted match with " + challenges[ctx.message.author.id]["p2name"] + ".")
                        return await bot.say("You must both report the score using !win @[opponent] if you won and !lose @[opponent] if you lost!")
                challenges[ctx.message.author.id] = {
                "p1name": ctx.message.author.name,
                "p2id": member.id,
                "p2name": member.name,
                "p1report": 0,
                "p2report": 0,
                "p2accept": 0
                }
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()

            await bot.say("Please note you can only challenge one person at a time (for now)")
            return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")
            # other guy must accept
            # then when they finish they have to let the bot know who won
            # then trueskill happens!

@bot.command(pass_context=True)
async def accept(ctx, member : discord.Member):
    if os.path.isfile("challenges.json") == False:
        return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you or is challenging someone else.")
    else:
        f = open("challenges.json", "r")
        s = f.read()
        challenges = json.loads(s)
        f.close()
        if (member.id in challenges) == False:
            return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you or is challenging someone else.")
        if challenges[member.id]["p2id"] == ctx.message.author.id:
            if challenges[member.id]["p2accept"] == 1:
                return await bot.say("you've already accepted the match!\nTo report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            challenges[member.id]["p2accept"] = 1
            f = open("challenges.json", "w")
            s = json.dumps(challenges)
            with open ("challenges.json", "w") as f:
                f.write(s)
            f.close()
            await bot.say(ctx.message.author.mention + " has accepted " + member.mention + "'s challenge!")
            return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
        return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you or is challenging someone else.")

@bot.command(pass_context=True)
async def win(ctx, member : discord.Member):
    if os.path.isfile("challenges.json") == False:
        return await bot.say(ctx.message.author.mention + ", there are no active challenges.")
    else:
        f = open("challenges.json", "r")
        s = f.read()
        challenges = json.loads(s)
        if ctx.message.author.id in challenges:
            if challenges[ctx.message.author.id]["p2id"] != member.id or challenges[ctx.message.author.id]["p2accept"] != 1:
                if member.id in challenges:
                    if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member]["p2accept"] == 1:
                        p1 = member
                        p2 = ctx.message.author
                    else:
                        return await bot.say("You do not have an active match with " + member.name + ".")
                else:
                    return await bot.say("You do not have an active match with " + member.name + ".")


            else:
                p1 = ctx.message.author
                p2 = member
        else:
            if (member.id in challenges) == False:
                return await bot.say("You do not have an active match with " + member.name + ".")
            else:
                if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member.id]["p2accept"] == 1:
                    p1 = member
                    p2 = ctx.message.author
                else:
                    return await bot.say("You do not have an active match with " + member.name + ".")

        ############

        if p2 == member:
            challenges[p1.id]["p1report"] = 1
            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
                await bot.say(p1.name + " won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return #p1 won. trueskill time
            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):
                challenges[p1.id]["p1report"] = 0
                challenges[p1.id]["p2report"] = 0
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            else:
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()

                return await bot.say("Thank you for reporting the score. Waiting for " + p2.mention + " to report!")
        else:
            challenges[p1.id]["p2report"] = 1
            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
                await bot.say(p2.name + "won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return #p2 won. trueskill time
            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):

                challenges[p1.id]["p1report"] = 0
                challenges[p1.id]["p2report"] = 0
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            else:
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return await bot.say("Thank you for reporting the score. Waiting for " + p1.mention + " to report!")

@bot.command(pass_context=True)
async def lose(ctx, member : discord.Member):
    if os.path.isfile("challenges.json") == False:
        return await bot.say(ctx.message.author.mention + ", there are no active challenges.")
    else:
        f = open("challenges.json", "r")
        s = f.read()
        challenges = json.loads(s)
        if ctx.message.author.id in challenges:
            if challenges[ctx.message.author.id]["p2id"] != member.id or challenges[ctx.message.author.id]["p2accept"] != 1:
                if member.id in challenges:
                    if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member]["p2accept"] == 1:
                        p1 = member
                        p2 = ctx.message.author
                    else:
                        return await bot.say("You do not have an active match with " + member.name + ".")
                else:
                    return await bot.say("You do not have an active match with " + member.name + ".")


            else:
                p1 = ctx.message.author
                p2 = member
        else:
            if (member.id in challenges) == False:
                return await bot.say("You do not have an active match with " + member.name + ".")
            else:
                if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member.id]["p2accept"] == 1:
                    p1 = member
                    p2 = ctx.message.author
                else:
                    return await bot.say("You do not have an active match with " + member.name + ".")

        ############

        if p2 == member:
            challenges[p1.id]["p1report"] = -1
            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
                await bot.say(p2.name + "won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return #p2 won. trueskill time and delete challenge
            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):
                challenges[p1.id]["p1report"] = 0
                challenges[p1.id]["p2report"] = 0
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            else:
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()

                return await bot.say("Thank you for reporting the score. Waiting for " + p2.mention + " to report!")
        else:
            challenges[p1.id]["p2report"] = -1
            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
                await bot.say(p1.name + " won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return #p1 won. trueskill time
            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):

                challenges[p1.id]["p1report"] = 0
                challenges[p1.id]["p2report"] = 0
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            else:
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return await bot.say("Thank you for reporting the score. Waiting for " + p1.mention + " to report!")




bot.run("Mjk3MTA2MjcwMDc3NTgzNDAx.C78Vqg.7mwzkkPmwP1MxFJ1Oqr51AxPpjg")

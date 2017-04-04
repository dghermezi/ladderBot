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
#leaderboards
#make it so you cant challenge/be challenged/accept a match if youre currently in one
#cancel matches without forfeit? up to tempo i guess
#proper documentation
#let someone challenge more than one user at a time
#clean up messy code/use functions/methods
#decay



logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = Bot(command_prefix="!")
ts = trueskill.TrueSkill(draw_probability = 0.00)
SCORE_MULTIPLYER = 1000

@bot.event
async def on_read():
    print("Client logged in")

@bot.command(pass_context=True)
async def register(ctx):

    if os.path.isfile("users.json") == False:
        users = {}
        users[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "mu": 25.0,
        "sigma": 8.333,
        "score": 0,
        "matched": 0,
        "wins": 0,
        "losses": 0
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
                    "mu": 25.0,
                    "sigma": 8.333,
                    "score": 0,
                    "matched": 0,
                    "wins": 0,
                    "losses": 0
                    }
            f = open("users.json" ,"w")
            s = json.dumps(users)
            with open("users.json", "w") as f:
                f.write(s)
            f.close()
            return await bot.say(ctx.message.author.name + " is now registered!")

@bot.command()
async def score(member : discord.Member):
    if os.path.isfile("users.json") == False:
        return await bot.say(member.name + " is not registered!")
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if member.id in users:
            score = users[member.id]["score"]
            if score < 1:
                return await bot.say(member.name + " has a score of 0!")
            else:
                return await bot.say(member.name + " has a score of " + str(int(SCORE_MULTIPLYER * score)) + "!")
        else:
            return await bot.say(member.name + " is not registered!")

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
                if users[ctx.message.author.id]["matched"] == 1:
                    if (ctx.message.author.id in challenges):
                        if challenges[ctx.message.author.id]["p2accept"] == 1:
                            await bot.say(ctx.message.author.mention + ", you already have an accepted match with " + challenges[ctx.message.author.id]["p2name"] + ".")
                            return await bot.say("You must both report the score using !win @[opponent] if you won and !lose @[opponent] if you lost!")
                    for oppID in challenges:
                        if challenges[oppID]["p2accept"] == 1 and challenges[oppID]["p2id"] == ctx.message.author.id:
                            return await bot.say("You've already accepted a challenge from " + users[oppID]["name"] + "! Please finish that match first!")
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
                return await bot.say("You've already accepted the match!\nTo report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
            challenges[member.id]["p2accept"] = 1
            f = open("users.json" , "r")
            s = f.read()
            f.close()
            users = json.loads(s)

            if users[ctx.message.author.id]["matched"] == 1:
                return await bot.say("You've already accepted a match! Please finish your other match first!")

            users[ctx.message.author.id]["matched"] == 1
            users[member.id]["matched"] == 1
            f = open("users.json", "w")
            s = json.dumps(users)
            with open ("users.json", "w") as f:
                f.write(s)
            f.close()


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
                return updateScores(p1, p2)
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
                await bot.say(p2.name + " won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return updateScores(p2, p1)
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
                await bot.say(p2.name + " won!")
                del challenges[p1.id]
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()
                return updateScores(p2, p1)
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
                return updateScores(p1,p2)
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

def updateScores(winner : discord.Member, loser : discord.Member):
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    winnerMu = users[winner.id]["mu"]
    winnerSigma = users[winner.id]["sigma"]
    loserMu = users[loser.id]["mu"]
    loserSigma = users[loser.id]["sigma"]
    winnerRating = ts.create_rating(mu=winnerMu, sigma = winnerSigma)
    loserRating = ts.create_rating(mu = loserMu, sigma = loserSigma)
    winnerRating, loserRating = ts.rate_1vs1(winnerRating, loserRating)

    users[winner.id]["mu"] = winnerRating.mu
    users[winner.id]["sigma"] = winnerRating.sigma
    users[winner.id]["score"] =ts.expose(winnerRating)
    users[loser.id]["mu"] = loserRating.mu
    users[loser.id]["sigma"] = loserRating.sigma
    users[loser.id]["score"] = ts.expose(loserRating)
    users[winner.id]["wins"] += 1
    users[loser.id]["losses"] += 1
    users[winner.id]["matched"] = 0
    users[loser.id]["matched"] = 0

    f = open("users.json", "w")
    s = json.dumps(users)
    with open("users.json", "w"):
        f.write(s)
    f.close()

    f = open("challenges.json", "r")
    s = f.read()
    challenges = json.loads(s)
    f.close()
    if winner.id in challenges:
        del challenges[winner.id]
    if loser.id in challenges:
        del challenges[loser.id]
    f = open("challenges.json" ,"w")
    s = json.dumps(challenges)
    with open("challenges.json", "w"):
        f.write(s)
    f.close()


bot.run("Mjk3MTA2MjcwMDc3NTgzNDAx.C78Vqg.7mwzkkPmwP1MxFJ1Oqr51AxPpjg")

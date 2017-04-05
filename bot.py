# Author: David G. (Videowaffles)
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import logging
import json
import os.path
import trueskill
import operator
import time

#things left to implement
#
#proper documentation
#clean up messy code/use functions/methods
#decay

description = '''Ladder system implemented using trueskill. Currently in beta. Message @Videowaffles#3628 to report bugs/make suggestions'''

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = Bot(command_prefix="!", description = description)
ts = trueskill.TrueSkill(draw_probability = 0.00)
SCORE_MULTIPLYER = 1000

@bot.event
async def on_read():
    print("Client logged in")

@bot.command(pass_context=True)
async def register(ctx):
    """Registers a user\n"""

    if os.path.isfile("users.json") == False:
        users = {}
        users[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "mu": 25.0,
        "sigma": 8.333,
        "score": 0,
        "matched": 0,
        "wins": 0,
        "losses": 0,
        "mention": ctx.message.author.mention
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
                    "losses": 0,
                    "mention": ctx.message.author.mention
                    }
            f = open("users.json" ,"w")
            s = json.dumps(users)
            with open("users.json", "w") as f:
                f.write(s)
            f.close()
            return await bot.say(ctx.message.author.name + " is now registered!")

@bot.command()
async def score(member : discord.Member):
    """Shows score of a registered member"""

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
    """Challenges a member to a match"""
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
                challenges[1] = {
                "p1id": ctx.message.author.id,
                "p1name": ctx.message.author.name,
                "p2id": member.id,
                "p2name": member.name,
                "p1report": 0,
                "p2report": 0,
                "p2accept": 0,
                "p1cancel": 0,
                "p2cancel": 0
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
                    for i in challenges:
                        if challenges[i]["p1id"] == ctx.message.author.id and challenges[i]["p2accept"] == 1:
                            await bot.say(ctx.message.author.mention + ", you have already started a match with " + challenges[i]["p2name"] + ".")
                            return await bot.say("You must both report the score using '!win @[winner]'.")
                        if challenges[i]["p2id"] == ctx.message.author.id and challenges[i]["p2accept"] == 1:
                            await bot.say(ctx.message.author.mention + ", you have already started a match with " + challenges[i]["p1name"] + ".")
                            return await bot.say("You must both report the score using '!win @[winner]'.")

                for i in challenges:
                    if challenges[i]["p1id"] == ctx.message.author.id and challenges[i]["p2id"] == member.id:
                        return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")
                    if challenges[i]["p2id"] == ctx.message.author.id and challenges[i]["p1id"] == member.id:
                        return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")

                i = 1
                while i in challenges:
                    i += 1
                challenges[i] = {
                "p1id": ctx.message.author.id,
                "p1name": ctx.message.author.name,
                "p2id": member.id,
                "p2name": member.name,
                "p1report": 0,
                "p2report": 0,
                "p2accept": 0,
                "p1cancel": 0,
                "p2cancel": 0
                }
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()

            #await bot.say("Please note you can only challenge one person at a time (for now)")
            return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")
            # other guy must accept
            # then when they finish they have to let the bot know who won
            # then trueskill happens!

@bot.command(pass_context=True)
async def accept(ctx, member : discord.Member):
    """Accepts a challenge from a member"""
    if os.path.isfile("challenges.json") == False:
        return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you or is challenging someone else.")
    else:
        f = open("users.json" , "r")
        s = f.read()
        f.close()
        users = json.loads(s)
        if users[ctx.message.author.id]["matched"] == 1:
            return await bot.say("You've already accepted a match! Please finish your other match first!")
        f = open("challenges.json", "r")
        s = f.read()
        challenges = json.loads(s)
        f.close()
        found = 0
        for i in challenges:
            if found == 0:
                if challenges[i]["p2id"] == ctx.message.author.id:
                    if challenges[i]["p1id"] == member.id:
                        if challenges[i]["p2accept"] == 1:
                            return await bot.say("You've already accepted the match!\nTo report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
                        else:
                            found = 1
                            challenges[i]["p2accept"] = 1
                            users[ctx.message.author.id]["matched"] = 1
                            users[member.id]["matched"] = 1
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

        if found == 0:
            return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you. Cannot accept.")

        return await bot.say(ctx.message.author.mention + " has accepted " + member.mention + "'s challenge!\nTo report score, simply type '!win @[winner]'")

@bot.command(pass_context=True)
async def win(ctx, member : discord.Member):
    """Report the winner of a match"""
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()

    if users[ctx.message.author.id]["matched"] == 0 or users[member.id]["matched"] == 0:
        return await bot.say("You are not in a match with " + member.name + ".")

    f = open("challenges.json", "r")
    s = f.read()
    challenges = json.loads(s)
    f.close()
    found = 0
    matchID = 0
    winnerID = member.id
    loserID = ctx.message.author.id
    if ctx.message.author.id == member.id:
        for i in challenges:
            if found == 0:
                if challenges[i]["p1id"] == winnerID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    loserID = challenges[i]["p2id"]
                    challenges[i]["p1report"] = 1
                elif challenges[i]["p2id"] == winnerID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    loserID = challenges[i]["p1id"]
                    challenges[i]["p2report"] = 1
    else:
        for i in challenges:
            if found == 0:
                if challenges[i]["p1id"] == loserID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    challenges[i]["p1report"] = -1
                elif challenges[i]["p2id"] == loserID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    challenges[i]["p2report"] = -1


    if found == 0:
        return await bot.say("No match was found.")

    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()

    if challenges[matchID]["p1report"] + challenges[matchID]["p2report"] == 0:
        await bot.say(users[winnerID]["name"] + " won!")
        del challenges[matchID]
        f = open("challenges.json", "w")
        s = json.dumps(challenges)
        with open ("challenges.json", "w") as f:
            f.write(s)
        f.close()
        return updateScores(winnerID, loserID)
    elif (challenges[matchID]["p1report"] + challenges[matchID]["p2report"] == 2) or (challenges[matchID]["p1report"] + challenges[matchID]["p2report"] == -2):
        challenges[matchID]["p1report"] = 0
        challenges[matchID]["p2report"] = 0
        f = open("challenges.json", "w")
        s = json.dumps(challenges)
        with open("challenges.json", "w") as f:
            f.write(s)
        f.close()
        await bot.say("You reported opposite outcomes. Please report again!")
        return await bot.say("To report score, simply type '!win @[winner]'")
    else:
        f = open("challenges.json", "w")
        s = json.dumps(challenges)
        with open("challenges.json", "w") as f:
            f.write(s)
        f.close()

        return await bot.say("Thank you for reporting the score. Waiting for your opponnent to report!")

#@bot.command(pass_context=True)
#async def lose(ctx, member : discord.Member):
#    """Report match against a member as a loss for you"""
#    if os.path.isfile("challenges.json") == False:
#        return await bot.say(ctx.message.author.mention + ", there are no active challenges.")
#    else:
#        f = open("challenges.json", "r")
#        s = f.read()
#        challenges = json.loads(s)
#        if ctx.message.author.id in challenges:
#            if challenges[ctx.message.author.id]["p2id"] != member.id or challenges[ctx.message.author.id]["p2accept"] != 1:
#                if member.id in challenges:
#                    if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member]["p2accept"] == 1:
#                        p1 = member
#                        p2 = ctx.message.author
#                    else:
#                        return await bot.say("You do not have an active match with " + member.name + ".")
#                else:
#                    return await bot.say("You do not have an active match with " + member.name + ".")


#            else:
#                p1 = ctx.message.author
#                p2 = member
#        else:
#            if (member.id in challenges) == False:
#                return await bot.say("You do not have an active match with " + member.name + ".")
#            else:
#                if challenges[member.id]["p2id"] == ctx.message.author.id and challenges[member.id]["p2accept"] == 1:
#                    p1 = member
#                    p2 = ctx.message.author
#                else:
#                    return await bot.say("You do not have an active match with " + member.name + ".")

        ############

#        if p2 == member:
#            challenges[p1.id]["p1report"] = -1
#            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
#                await bot.say(p2.name + " won!")
#                del challenges[p1.id]
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open ("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()
#                return updateScores(p2, p1)
#            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):
#                challenges[p1.id]["p1report"] = 0
#                challenges[p1.id]["p2report"] = 0
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()
#                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
#                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
#            else:
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()

#                return await bot.say("Thank you for reporting the score. Waiting for " + p2.mention + " to report!")
#        else:
#            challenges[p1.id]["p2report"] = -1
#            if challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 0:
#                await bot.say(p1.name + " won!")
#                del challenges[p1.id]
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open ("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()
#                return updateScores(p1,p2)
#            elif (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == 2) or (challenges[p1.id]["p1report"] + challenges[p1.id]["p2report"] == -2):

#                challenges[p1.id]["p1report"] = 0
#                challenges[p1.id]["p2report"] = 0
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()
#                await bot.say(p1.mention + ", " + p2.mention + ", you reported opposite outcomes. Please report again!")
#                return await bot.say("To report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
#            else:
#                f = open("challenges.json", "w")
#                s = json.dumps(challenges)
#                with open("challenges.json", "w") as f:
#                    f.write(s)
#                f.close()
#                return await bot.say("Thank you for reporting the score. Waiting for " + p1.mention + " to report!")

def updateScores(winner : discord.Member.id, loser : discord.Member.id):
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    winnerMu = users[winner]["mu"]
    winnerSigma = users[winner]["sigma"]
    loserMu = users[loser]["mu"]
    loserSigma = users[loser]["sigma"]
    winnerRating = ts.create_rating(mu=winnerMu, sigma = winnerSigma)
    loserRating = ts.create_rating(mu = loserMu, sigma = loserSigma)
    winnerRating, loserRating = ts.rate_1vs1(winnerRating, loserRating)

    users[winner]["mu"] = winnerRating.mu
    users[winner]["sigma"] = winnerRating.sigma
    users[winner]["score"] =ts.expose(winnerRating)
    users[loser]["mu"] = loserRating.mu
    users[loser]["sigma"] = loserRating.sigma
    users[loser]["score"] = ts.expose(loserRating)
    users[winner]["wins"] += 1
    users[loser]["losses"] += 1
    users[winner]["matched"] = 0
    users[loser]["matched"] = 0

    f = open("users.json", "w")
    s = json.dumps(users)
    with open("users.json", "w"):
        f.write(s)
    f.close()

@bot.command(pass_context=True)
async def leaderboard(ctx):
    """Shows the current top 10 and their scores"""
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    lb = {}
    for user in users:
        if users[user]["score"] < 1:
            lb[users[user]["name"]] = 0
        else:
            lb[users[user]["name"]] = int(1000 * ts.expose(ts.create_rating(mu=users[user]["mu"], sigma=users[user]["sigma"])))

    sortedlb = sorted(lb.items(), key=operator.itemgetter(1), reverse = True)

    s = "```\nLeaderboard:"
    i = 0
    for user in sortedlb:
        i += 1
        s += "\n{:>3}: Name:  {:<20}\tscore:  {:<10}".format(str(i), user[0], str(user[1]))

    s += "\n```"
    return await bot.send_message(ctx.message.channel, s)

@bot.command(pass_context=True)
async def cancel(ctx):
    """If not in a match, cancels all of your outgoing challenges. If in a match, opponent must cancel as well"""
    p1 = ctx.message.author
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    f = open("challenges.json", "r")
    s = f.read()
    challenges = json.loads(s)
    f.close()
    f = open("anycoy.json", "r")
    s = f.read()
    anycoy = json.loads(s)
    f.close()
    del anycoy[p1.id]
    f = open("anycoy.json", "w")
    s = json.dumps(anycoy)
    with open("anycoy.json", "w") as f:
        f.write(s)
    f.close()

    if p1.id in users:
        if users[p1.id]["matched"] == 0:
            for challenge in list(challenges):
                if challenges[challenge]["p1id"] == p1.id:
                    del challenges[challenge]
            f = open("challenges.json", "w")
            s = json.dumps(challenges)
            with open("challenges.json", "w") as f:
                f.write(s)
            f.close()
            return await bot.say("Canceled all your challenge requests.\nNote, you can still accept challenges from others who have challenged you before your cancel.")
        else:
            for challenge in list(challenges):
                if (challenges[challenge]["p1id"] == p1.id) and (challenges[challenge]["p2accept"] == 1):
                    if challenges[challenge]["p2cancel"] == 1:
                        users[p1.id]["matched"] = 0
                        users[challenges[challenge]["p2id"]]["matched"] = 0
                        opName = challenges[challenge]["p2name"]
                        del challenges[challenge]
                        f = open("challenges.json", "w")
                        s = json.dumps(challenges)
                        with open("challenges.json", "w") as f:
                            f.write(s)
                        f.close()
                        f = open("users.json", "w")
                        s = json.dumps(users)
                        with open("users.json", "w") as f:
                            f.write(s)
                        f.close()
                        print("hi")
                        return await bot.say("Canceled " + p1.name + " and " + opName + "'s match.")
                    else:
                        challenges[challenge]["p1cancel"] = 1
                        f = open("challenges.json", "w")
                        s = json.dumps(challenges)
                        with open("challenges.json", "w") as f:
                            f.write(s)
                        f.close()
                        return await bot.say(challenges[challenge]["p2name"] + " must also cancel for the match to be canceled.")
                elif challenges[challenge]["p2id"] == p1.id and challenges[challenge]["p2accept"] == 1:
                    challenges[challenge]["p2cancel"] = 1
                    if challenges[challenge]["p1cancel"] == 1:
                        users[p1.id]["matched"] = 0
                        users[challenges[challenge]["p1id"]]["matched"] = 0
                        opName = challenges[challenge]["p1name"]
                        del challenges[challenge]
                        f = open("challenges.json", "w")
                        s = json.dumps(challenges)
                        with open("challenges.json", "w") as f:
                            f.write(s)
                        f.close()
                        f = open("users.json", "w")
                        s = json.dumps(users)
                        with open("users.json", "w") as f:
                            f.write(s)
                        f.close()
                        return await bot.say("Canceled "  + opName + " and " + p1.name+ "'s match.")
                    else:
                        f = open("challenges.json", "w")
                        s = json.dumps(challenges)
                        with open("challenges.json", "w") as f:
                            f.write(s)
                        f.close()
                        return await bot.say(challenges[challenge]["p1name"] + " must also cancel for the match to be canceled.")

    else:
        return await bot.say("You have are not registered!")


@bot.command(pass_context=True)
async def anycoy(ctx):
    """Looks for an opponent"""
    #test = int(round(time.time()))
    #while (int(round(time.time())) - test < 60):
    #    print("a")
    #print("done")
    if os.path.isfile("anycoy.json") == False:
        anycoy = {}
        anycoy[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "time": int(round(time.time()))
        }
        f = open("anycoy.json", "w+")
        s = json.dumps(anycoy)
        with open("anycoy.json", "w+") as f:
            f.write(s)
        f.close()
        return await bot.say("No one else is looking to play right now :(")
    else:
        f = open("anycoy.json", "r")
        s = f.read()
        anycoy = json.loads(s)
        f.close()
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()

        for user in list(anycoy):
            if int(round(time.time())) - anycoy[user]["time"] > 600:
                del anycoy[user]
        anycoy[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "time": int(round(time.time()))
        }
        f = open("anycoy.json", "w")
        s = json.dumps(anycoy)
        with open("anycoy.json", "w") as f:
            f.write(s)
        f.close()
        found = 0
        quality = 0
        name = ""
        allUsers = ""
        p1 = ts.create_rating(mu=users[ctx.message.author.id]["mu"], sigma = users[ctx.message.author.id]["sigma"])
        for user in anycoy:
            if user != ctx.message.author.id:
                found += 1
                allUsers += users[user]["mention"] + "\t"
                p2 = ts.create_rating(mu=users[user]["mu"], sigma=users[user]["sigma"])
                if ts.quality_1vs1(p1, p2) > quality:
                    quality = ts.quality_1vs1(p1,p2)
                    name = users[user]["name"]
        if found > 0:
            return await bot.say("Your best match would be with " + users[user]["mention"] + ".\nAll users looking for a match right now: " + allUsers + "\nType '!challenge @[opponent] to challenge someone!'")
        else:
            return await bot.say("No one else is looking to play right now :(")


bot.run("Mjk4NjI5NTg0MTk3MjU1MTc4.C8Ww9Q.rDlxzAqSebCNR0zj9rkrwIBWCKc")

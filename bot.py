# Author: David G. (@Videowaffles#3628)
import discord
from discord.ext.commands import Bot
from discord.ext import commands
import logging
import json
import os.path
import trueskill
import operator
import time

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
                    #if challenges[i]["p2id"] == ctx.message.author.id and challenges[i]["p1id"] == member.id:
                        return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")

                i = 1
                while str(i) in challenges:
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

            return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")

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

    if os.path.isfile("match_history.json") == False:
        i = 1
        history = {}
        history[i] = {
        "winnerID": winner,
        "winnerName": users[winner]["name"],
        "loserName": users[loser]["name"],
        "loserID": loser,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        f = open("match_history.json", "w+")
        s = json.dumps(history)
        with open("match_history.json", "w+") as f:
            f.write(s)
        f.close()
    else:
        f = open("match_history.json", "r")
        s = f.read()
        history = json.loads(s)
        f.close()
        i = 1
        print(type(i))
        while str(i) in history:
            i += 1
        history[i] = {
        "winnerID": winner,
        "winnerName": users[winner]["name"],
        "loserName": users[loser]["name"],
        "loserID": loser,
        "time": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }
        f = open("match_history.json", "w")
        s = json.dumps(history)
        with open("match_history.json", "w") as f:
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
    if p1.id in anycoy:
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
    """Looks for an opponent. Places you in a 'queue' for 10 minutes"""
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)

    if (ctx.message.author.id in users) == False:
        print(ctx.message.author.id in users == False)
        return await bot.say("You must register first. Type !register")
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
        return await bot.say("Placed you in the queue!\nNo one else is looking to play right now :(")
    else:
        f = open("anycoy.json", "r")
        s = f.read()
        anycoy = json.loads(s)
        f.close()
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()


        anycoy[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "time": int(round(time.time()))
        }
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
                    name = users[user]["mention"]
        if found > 0:
            return await bot.say("Placed you in the queue!\nYour best match would be with " + name + ".\nAll users looking for a match right now: " + allUsers + "\nType '!challenge @[opponent]' to challenge someone!")
        else:
            return await bot.say("Placed you in the queue!\nNo one else is looking to play right now :(")

@bot.command(pass_context=True)
async def history(ctx):
    """Whispers you your match history"""
    user = ctx.message.author
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    string =  "```\nTotal Wins:  " + str(users[user.id]["wins"]) + "   |   Total Losses:  " + str(users[user.id]["losses"]) + "\n"
    f=open("match_history.json", "r")
    s = f.read()
    history = json.loads(s)
    f.close()
    for match in history:
        if history[match]["winnerID"] == ctx.message.author.id:
            string += "\nWIN against " + history[match]["loserName"] + " on " + history[match]["time"]
        elif history[match]["loserID"] == ctx.message.author.id:
            string +=  "\nLOSS to " + history[match]["loserName"] + " on " + history[match]["time"]
    string += "\n```"
    return await bot.send_message(user, string)


bot.run("Mjk4NjI5NTg0MTk3MjU1MTc4.C8beXQ.RYxOkPkC4q43kd4tUEV1_U9lUEE")

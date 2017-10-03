# Author: David G. (@Videowaffles#3628)
# See https://github.com/dghermezi/ladderBot README for more info
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

# formatting for log event file
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# the bot will respond to commands with ! before the keyword
bot = Bot(command_prefix="!", description = description)

# in melee, draws are impossible.
ts = trueskill.TrueSkill(draw_probability = 0.00)

# will multiply the trueskill score by 1000 to make data nicer
SCORE_MULTIPLYER = 1000

@bot.event
async def on_read():
    print("Client logged in")

# !register will create a new user with default trueskill fields
@bot.command(pass_context=True)
async def register(ctx):
    """Registers a user\n"""

    # if this is the first user, then we need to creat the json file
    if os.path.isfile("users.json") == False:
        users = {}
        # create the new user
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
        # save the new users.json file
        f = open("users.json", "w+")
        s = json.dumps(users)
        with open ("users.json", "w+") as f:
            f.write(s)
        f.close()
        return await bot.say(ctx.message.author.name + " is now registered!")

    # if users.json already exists, open it, add the user, and save it
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

# !score checks the users.json file and looks up the score of a user
@bot.command()
async def score(member : discord.Member):
    """Shows score of a registered member"""

    # if the file doesnt exist, then obviously no user has been registered yet
    if os.path.isfile("users.json") == False:
        return await bot.say(member.name + " is not registered!")
    # otherwise, open users.json, load the json objects, and close the file
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        # find the user, get the score, and display it
        if member.id in users:
            score = users[member.id]["score"]
            if score < 1:
                return await bot.say(member.name + " has a score of 0!")
            else:
                return await bot.say(member.name + " has a score of " + str(int(SCORE_MULTIPLYER * score)) + "!")
        # the user could not be found in the json object, so the user has not registered yet
        else:
            return await bot.say(member.name + " is not registered!")

# !challenge creates a challenge request between two registered users
@bot.command(pass_context=True)
async def challenge(ctx, member : discord.Member):
    """Challenges a member to a match"""

    # first, we need to check that users.json exists, and that you arent challenging yourself
    if ctx.message.author.id == member.id:
        return await bot.say("You can't challenge yourself!")
    if os.path.isfile("users.json") == False:
        return await bot.say("You're not registered!")

    # next, open users.json and check if the opponent is registered
    # we already checked if users.json exists, so we open it and check if both users have been registered
    else:
        f = open("users.json", "r")
        s = f.read()
        users = json.loads(s)
        f.close()
        if (ctx.message.author.id in users) == False:
            return await bot.say("You're not registered!")
        if (member.id in users) == False:
            return await bot.say(member.name + " is not registered!")

        # the challenges are stored in their own json file called challenges.json
        else:
            # if it doesnt exist, create it. a challenge keeps track of the users Discord IDs and names
            # as well as if the challenge has been accepted, canceled, or the outcome was reported.
            # We keep track of all of this to make sure both users agree to play, as well as on the outcome.
            # We keep the user ID as well as the name because the IDs are unique but the names may not be
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
                # dump the object into a json object and save the file
                s = json.dumps(challenges)
                with open ("challenges.json", "w+") as f:
                    f.write(s)
                f.close()

            # if the file exists, open it
            else:
                f = open("challenges.json", "r")
                s = f.read()
                challenges = json.loads(s)

                # first, make sure that both users are not already in a match
                # we check if the user that called the challenge is in a match
                # if so, we find the match
                if users[ctx.message.author.id]["matched"] == 1:
                    for i in challenges:

                        # this case is when the challenging user has already challenged someone else who has accepted
                        if challenges[i]["p1id"] == ctx.message.author.id and challenges[i]["p2accept"] == 1:
                            await bot.say(ctx.message.author.mention + ", you have already started a match with " + challenges[i]["p2name"] + ".")
                            return await bot.say("You must both report the score using '!win @[winner]'.")

                        # this case is when the challenging user has already accepted another user's challenge
                        if challenges[i]["p2id"] == ctx.message.author.id and challenges[i]["p2accept"] == 1:
                            await bot.say(ctx.message.author.mention + ", you have already started a match with " + challenges[i]["p1name"] + ".")
                            return await bot.say("You must both report the score using '!win @[winner]'.")

                # next, we check if this challenge between users already exists. if so, just repeat the message. no need to make a new challenge
                for i in challenges:
                    if challenges[i]["p1id"] == ctx.message.author.id and challenges[i]["p2id"] == member.id:
                        return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")
                    if challenges[i]["p2id"] == ctx.message.author.id and challenges[i]["p1id"] == member.id:
                        return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")

                i = 1 # this is the challenge id number. find the smalled available number
                while str(i) in challenges:
                    i += 1
                # then create a challenge with that id between the two users
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
                # and save the updated challenges.json
                f = open("challenges.json", "w")
                s = json.dumps(challenges)
                with open ("challenges.json", "w") as f:
                    f.write(s)
                f.close()

            return await bot.say(ctx.message.author.mention + " is challenging " + member.mention +"\ntype '!accept @[challenger]' to accept!")

# !accept lets a user accept a challenge from another user
@bot.command(pass_context=True)
async def accept(ctx, member : discord.Member):
    """Accepts a challenge from a member"""

    # open the challenges.json file if it exists
    if os.path.isfile("challenges.json") == False:
        return await bot.say(ctx.message.author.mention + ", " + member.name + " didn't challenge you or is challenging someone else.")
    else:
        f = open("users.json" , "r")
        s = f.read()
        f.close()
        users = json.loads(s)
        # make sure the user is not already in an active match
        if users[ctx.message.author.id]["matched"] == 1:
            return await bot.say("You've already accepted a match! Please finish your other match first!")
        f = open("challenges.json", "r")
        s = f.read()
        challenges = json.loads(s)
        f.close()

        # go through every challenge in the json object until we find the one between the two users
        found = 0
        for i in challenges:
            if found == 0:
                if challenges[i]["p2id"] == ctx.message.author.id:
                    if challenges[i]["p1id"] == member.id:

                        # if we found the challenge, but it has already been accepted, tell them to report the score
                        if challenges[i]["p2accept"] == 1:
                            return await bot.say("You've already accepted the match!\nTo report score, the winner must type '!win @[opponent]' and the loser must type '!lose @[opponent]'")
                        # otherwise, mark the challenge as accepted and the users as being in an active match
                        else:
                            found = 1
                            challenges[i]["p2accept"] = 1
                            users[ctx.message.author.id]["matched"] = 1
                            users[member.id]["matched"] = 1
                            # then save the updated users.json and challenges.json
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

# !win and is for reporting the outcome of a match. this was the best way i could think of that wasnt too complicated for users to report the results
# both users simply type !win [winner] to report the result
@bot.command(pass_context=True)
async def win(ctx, member : discord.Member):
    """Report the winner of a match"""
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()

    # first, we check if both of the users are in an active match
    if users[ctx.message.author.id]["matched"] == 0 or users[member.id]["matched"] == 0:
        return await bot.say("You are not in a match with " + member.name + ".")

    # if so, we open up challenges.json and find the match
    f = open("challenges.json", "r")
    s = f.read()
    challenges = json.loads(s)
    f.close()
    found = 0
    matchID = 0
    # the winner will always be the user tagged after the !win command
    # the loser is never tagged, so we have to figure out which user is the loser
    # start by assuming the user who called !win is the loser
    winnerID = member.id
    loserID = ctx.message.author.id

    # then we check if the user who called !win is the same as the user that is tagged after the !win command
    # this would mean that the user that called !win is the winner, not the loser, and we have to find the loser's ID in the challenges json
    if ctx.message.author.id == member.id:
        # so we go through all the challenges, look for an accepted challenge by the winner, and mark the other player in that challenge as the loser
        for i in challenges:
            if found == 0:
                if challenges[i]["p1id"] == winnerID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    loserID = challenges[i]["p2id"]
                    challenges[i]["p1report"] = 1 # a 1 means this user won, a -1 means this user lost
                elif challenges[i]["p2id"] == winnerID and challenges[i]["p2accept"] == 1:
                    found = 1
                    matchID = i
                    loserID = challenges[i]["p1id"]
                    challenges[i]["p2report"] = 1
    # this case is when the user who called !win is the one who lost
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

    # since we used 1 for a win and -1 for a loss, if both users reported the correct outcome, the result of adding them would be 0
    # if the both reported themselves as the winner, then the sum would be 2 and we would know it was reported incorrectly
    if challenges[matchID]["p1report"] + challenges[matchID]["p2report"] == 0:
        await bot.say(users[winnerID]["name"] + " won!")
        del challenges[matchID] # delete the existing challenge
        f = open("challenges.json", "w")
        s = json.dumps(challenges)
        with open ("challenges.json", "w") as f:
            f.write(s)
        f.close()
        return updateScores(winnerID, loserID) # update both users trueskill data
    # this case is when the result is reported incorrectly, so we reset the report and ask the users to report it again
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
    # this case is when only one person reported the match. simply save the json and wait for the other user to report
    else:
        f = open("challenges.json", "w")
        s = json.dumps(challenges)
        with open("challenges.json", "w") as f:
            f.write(s)
        f.close()

        return await bot.say("Thank you for reporting the score. Waiting for your opponnent to report!")

# this function uses Microsofts trueskill algorithm to update the trueskill of both users
def updateScores(winner : discord.Member.id, loser : discord.Member.id):
    # first we load all the user data we need
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)
    f.close()
    winnerMu = users[winner]["mu"]
    winnerSigma = users[winner]["sigma"]
    loserMu = users[loser]["mu"]
    loserSigma = users[loser]["sigma"]
    # then we create their trueskill rating from before the match
    winnerRating = ts.create_rating(mu=winnerMu, sigma = winnerSigma)
    loserRating = ts.create_rating(mu = loserMu, sigma = loserSigma)
    # finally, we create their new ratings with the results of the match
    winnerRating, loserRating = ts.rate_1vs1(winnerRating, loserRating)
    # then we save all the data back into the users object and save it to users.json
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

    # We also keep a file for match history! First we check if it already exists
    # if not, then we create a history json object, keep track of who won and who lost as well as what time it happened
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
        # and then we save the new file
        f = open("match_history.json", "w+")
        s = json.dumps(history)
        with open("match_history.json", "w+") as f:
            f.write(s)
        f.close()
    # otherwise, it already exists so open it up and add a new entry
    else:
        f = open("match_history.json", "r")
        s = f.read()
        history = json.loads(s)
        f.close()
        i = 1 # again, this is used to find the smallest available number
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

# This command simply opens up the users json file and sorts the users by their trueskill score
@bot.command(pass_context=True)
async def leaderboard(ctx):
    """Shows the current top 10 and their scores"""

    # Open up the users.json file, make a leaderboard object, and add every user to the leaderboard
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

    # now that every user is in the leaderboard, sort the leaderboard by score
    sortedlb = sorted(lb.items(), key=operator.itemgetter(1), reverse = True)

    # and simply output the results
    s = "```\nLeaderboard:"
    i = 0
    for user in sortedlb:
        i += 1
        s += "\n{:>3}: Name:  {:<20}\tscore:  {:<10}".format(str(i), user[0], str(user[1]))

    s += "\n```"
    return await bot.send_message(ctx.message.channel, s)

# This command cancels all of a users unaccepted outgoing challenges as well as requests a cancel on an already accepted match
@bot.command(pass_context=True)
async def cancel(ctx):
    """If not in a match, cancels all of your outgoing challenges. If in a match, opponent must cancel as well"""

    # open and load the users, challenges, and open challenges (anycoy)
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

    # if user was searching for anyone to play with (anycoy), then delete that request to play and save it
    if p1.id in anycoy:
        del anycoy[p1.id]
        f = open("anycoy.json", "w")
        s = json.dumps(anycoy)
        with open("anycoy.json", "w") as f:
            f.write(s)
        f.close()

    # if user is not in a match and has outgoing challenges, delete them
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
        # otherwise, the user is in a match, so we find if the user is p1 or p2 and mark the request to cancel.
        # if both p1 and p2 agree to cancel, then we delete the challenge
        else:
            for challenge in list(challenges):
                if (challenges[challenge]["p1id"] == p1.id) and (challenges[challenge]["p2accept"] == 1):
                    # if the other user already requested a cancel, then mark both users as not in a match and delete the challenge
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
                        return await bot.say("Canceled " + p1.name + " and " + opName + "'s match.")
                    # otherwise, mark that user wants to cancel and move on
                    else:
                        challenges[challenge]["p1cancel"] = 1
                        f = open("challenges.json", "w")
                        s = json.dumps(challenges)
                        with open("challenges.json", "w") as f:
                            f.write(s)
                        f.close()
                        return await bot.say(challenges[challenge]["p2name"] + " must also cancel for the match to be canceled.")
                # this is the same as above, but if the user was not the one to issue the original challenge, so the IDs are swapped
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

# marks a user as looking for a match. if multiple users are marked as looking for a match, then uses trueskill to suggest the best (closest) match
@bot.command(pass_context=True)
async def anycoy(ctx):
    """Looks for an opponent. Places you in a 'queue' for 10 minutes"""
    f = open("users.json", "r")
    s = f.read()
    users = json.loads(s)

    # first make sure the user is registered
    if (ctx.message.author.id in users) == False:
        print(ctx.message.author.id in users == False)
        return await bot.say("You must register first. Type !register")
    # we keep track of these active searches in anycoy.json
    # if it doesnt already exists, then this user is the only person searching for a match
    if os.path.isfile("anycoy.json") == False:
        anycoy = {}
        anycoy[ctx.message.author.id] = {
        "name": ctx.message.author.name,
        "time": int(round(time.time())) # since we dont want these searches to last forever, track when they were made
        }
        f = open("anycoy.json", "w+")
        s = json.dumps(anycoy)
        with open("anycoy.json", "w+") as f:
            f.write(s)
        f.close()
        return await bot.say("Placed you in the queue!\nNo one else is looking to play right now :(")
    # if the file arleady exists, open it. it is still possible that no other user is searching for a match, though
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
        # every time !anycoy is called, we check the list to find opponents.
        # the queue time is 10 minutes max, so first we must remove all users who last called !anycoy over 10 minutes ago (600 seconds)
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
        # we create a trueskill rating for the searching player, and save it. this is used to find matches of good quality
        p1 = ts.create_rating(mu=users[ctx.message.author.id]["mu"], sigma = users[ctx.message.author.id]["sigma"])
        # search the anycoy object for users that arent the original user.
        for user in anycoy:
            # when we find one, update how many we found, add the other user to the list of available matches, and check the quality of the match
            if user != ctx.message.author.id:
                found += 1
                allUsers += users[user]["mention"] + "\t"
                p2 = ts.create_rating(mu=users[user]["mu"], sigma=users[user]["sigma"])
                # if the quality of the match is better than the previous best quality, than update it and mark which user is the best match
                if ts.quality_1vs1(p1, p2) > quality:
                    quality = ts.quality_1vs1(p1,p2)
                    name = users[user]["mention"]
        if found > 0:
            return await bot.say("Placed you in the queue!\nYour best match would be with " + name + ".\nAll users looking for a match right now: " + allUsers + "\nType '!challenge @[opponent]' to challenge someone!")
        else:
            return await bot.say("Placed you in the queue!\nNo one else is looking to play right now :(")

# whispers a user their entire match history. This function is very basic.
# simply open up the history json and users json, build a string of output with the match history, and send it
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

# this is the bot's ID given by Discord
bot.run("Mjk4NjI5NTg0MTk3MjU1MTc4.C8beXQ.RYxOkPkC4q43kd4tUEV1_U9lUEE")

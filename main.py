import discord  # discord py library
import os  # thefuck idk
import pickle  # Fuckin makes me giggle ery tiem
from keep_alive import keep_alive  # keep the bot online while im not
from datetime import datetime  # lets me get time
from dotenv import load_dotenv  # lets us get the env file
from discord.ext import commands, tasks  # LEMME LOOP BABY
import re

dir = 'images/'  # store image directory to remove repitition
# usernames = []  #create empty username list
# nicks = []  #create empty nickname list
# remindTimes = ['0']  #remind times list
emptyList = []
load_dotenv()  # load the environment file


# right I stole this bit but it lets you type commands with any upper/lowercase combination
def mixedCase(*args):
    """
  Gets all the mixed case combinations of a string

  This function is for in-case sensitive prefixes
  """
    total = []
    import itertools
    for string in args:
        a = map(''.join,
                itertools.product(*((c.upper(), c.lower()) for c in string)))
        for x in list(a):
            total.append(x)

    return list(total)


TOKEN = os.getenv("TOKEN")  # get bots token from env file
bot = commands.Bot(
    case_insensitive=True,
    command_prefix=mixedCase('?'))  # only recognise messges after ?
bot.remove_command('help')  # basic help command is cank, Ima make my own

# creates the connection to discord
client = discord.Client()

# setting pfp
pfp_path = "images/Joy.png"
fp = open(pfp_path, "rb")
pfp = fp.read()

pickle_in1 = open("usernames.pickle", "rb")
usernames = pickle.load(pickle_in1)
pickle_in1.close()
pickle_in2 = open("nicks.pickle", "rb")
nicks = pickle.load(pickle_in2)
pickle_in2.close()
pickle_in3 = open("remindTimes.pickle", "rb")
remindTimes = pickle.load(pickle_in3)
pickle_in3.close()


# when the bot boots and is ready
@bot.event
async def on_ready():
    print('Ready To Heal!!')  # lemme know
    with open(pfp_path, "rb") as f:  # set profile pic
        pfp = f.read()
    await bot.user.edit(avatar=pfp)


# check the time every second
@tasks.loop(seconds=1)
async def reminder():
    message_channel = bot.get_channel(724634476034129991)
    current_time = datetime.strftime(datetime.utcnow(), "%H:%M:%S")
    # print(usernames)
    for i, remTime in enumerate(remindTimes):
        if remTime == current_time:
            id = usernames[i]
            fullID = "%s" % id
            await message_channel.send("{}, dont forget to take your meds today!".format(fullID))


# need this so the loop actually works
@reminder.before_loop
async def before():
    await bot.wait_until_ready()
    print("Finished waiting")


# start that LOOPY DOOPY baby
reminder.start()


# create my own help command instead
@bot.command()
async def help(ctx):
    author = ctx.message.author
    pfp = author.avatar_url
    uname = author.name

    # make it an embedded text
    embed = discord.Embed(
        colour=discord.Colour(0xFF69B4),
        title="NurseBot Command List",
        description="Below is a list of commands that incase you forgot!\u200B"
    )
    embed.set_author(
        name="{} Needed a little reminder, and that's ok!".format(uname),
        icon_url=pfp)
    embed.set_thumbnail(url="https://i.imgur.com/whhUiVV.png")
    embed.add_field(
        name="?help",
        value="The command you used to open this page :)",
        inline=False)
    embed.add_field(
        name="?remindme",
        value="Use this to be added to my reminder list",
        inline=False)
    embed.add_field(
        name="?users",
        value="See who I am making sure keeps healthy!",
        inline=False)
    embed.add_field(
        name="?remove",
        value="Want me to stop myself reminding you?",
        inline=False)
    embed.add_field(
        name="?mytime",
        value="Change the time you want me to remind you",
        inline=False)

    embed.set_footer(
        text="Information requested by: {}".format(ctx.author.display_name))
    await ctx.send(embed=embed)


# let users choose to be reminded
@bot.command()
async def remindMe(ctx):
    # Add user to list
    userId = ctx.author.id
    remUserId = "<@%s>" % userId
    usernames.append(remUserId)
    pickle_out1 = open("usernames.pickle", "wb")
    pickle.dump(usernames, pickle_out1)
    pickle_out1.close()
    await ctx.channel.send("Ok, I will remind you every day!")

    # Add users nickname to list
    userNick = ctx.author.nick
    nicks.append(userNick)
    pickle_out2 = open("nicks.pickle", "wb")
    pickle.dump(nicks, pickle_out2)
    pickle_out2.close()


@bot.command()
async def clear(ctx):
    pickle_out1 = open("usernames.pickle", "wb")
    pickle.dump(emptyList, pickle_out1)
    pickle_out1.close()
    pickle_out2 = open("nicks.pickle", "wb")
    pickle.dump(emptyList, pickle_out2)
    pickle_out2.close()
    pickle_out3 = open("remindTimes.pickle", "wb")
    pickle.dump(emptyList, pickle_out3)
    pickle_out3.close()


# let users remove from list
@bot.command()
async def remove(ctx):
    # remove from pinging list
    userId = ctx.author.id
    fullID = "<@%s>" % userId
    if fullID in usernames:
        index = usernames.index(fullID)
        remindTimes.pop(index)
        pickle_out3 = open("remindTimes.pickle", "wb")
        pickle.dump(remindTimes, pickle_out3)
        pickle_out3.close()
        usernames.remove(fullID)
        pickle_out1 = open("usernames.pickle", "wb")
        pickle.dump(usernames, pickle_out1)
        pickle_out1.close()
        await ctx.channel.send("Ok, I have removed you from my list. I hope you're better now!")

    else:
        await ctx.channel.send("I am not currently reminding you")

    # remove from Nickname list
    userNick = ctx.author.nick
    if userNick in nicks:
        nicks.remove(userNick)
        pickle_out2 = open("nicks.pickle", "wb")
        pickle.dump(nicks, pickle_out2)
        pickle_out2.close()
    else:
        await ctx.channel.send("I couldn't find your nickname anywhere :(")


# return users
@bot.command()
async def users(ctx):
    # return the nicknames of the users being reminded
    uNickg = repr(nicks)  # Convert the list to a string
    uNick0 = uNickg[1:-1]  # trim the brackets off the list
    uNick1 = uNick0.replace("'", "")  # remove the apostrophes
    uNick = uNick1.replace(",", " and")  # replace comma with and
    numRemind = len(usernames)  # get the length of the name list
    if numRemind > 0:  # if there are any names on there
        await ctx.channel.send("I am reminding: " + uNick)  # say who it reminds
        print("ID: %s" % usernames)
        print("Nicks: %s" % nicks)
        print("Times: %s" % remindTimes)
    else:  # if nobody is on the list
        await ctx.channel.send("I am not currently reminding anyone")  # say so


@bot.command()
async def myTime(ctx):
    input = ctx.message.content
    inp = input[8:]  # Make sure it's in the HH:MM:SS format

    matched = re.match("(?:[01]\d|2[0123]):(?:[012345]\d):(?:[012345]\d)", inp) # Regex
    is_match = bool(matched)
    print(is_match)
    if is_match:
        await ctx.channel.send("Ok, I will remind you at %s every day" % inp)
        userId = ctx.author.id
        fullID = "<@%s>" % userId  # get id
        if fullID in usernames:  # if id exists
            index = usernames.index(fullID)  # get the index of it
            numIndex = int(index)  # cast it as int
            print("Index Num: %s" % numIndex)

            # CHECK IF IT EXISTS
            timesLen = len(remindTimes)
            if timesLen > numIndex:
                remindTimes[numIndex] = inp
            else:
                remindTimes.insert(numIndex, inp)  # add time to corresponding times index
            print("Times List: %s" % remindTimes)
            pickle_outTime = open("remindTimes.pickle", "wb")
            pickle.dump(remindTimes, pickle_outTime)
            pickle_outTime.close()
        else:
            await ctx.channel.send("You need to sign up first! Try ?remindme")
        # await ctx.channel.send(inp)
    else:
        ctx.channel.send(
            "That time is not valid, please retype the command and enter it in the 24-hour format HH:MM:SS"
        )


# check if messages are NOT from the bot
@client.event
async def on_message(message):
    if message.author == client.user:
        return


keep_alive()
# Make the webserver run
bot.run(TOKEN)

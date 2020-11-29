import json
import os
import sys
import time
import traceback
from logging import Logger
import discord
import praw
from discord.ext import commands
import pathlib
import utils # noqa
os.chdir(f"{pathlib.Path(__file__).parent.absolute()}")

# Determining if we need to send a restart alert after everything is finished
if len(sys.argv) >= 2:
    channel_to_send = sys.argv[1]
else:
    channel_to_send = 0

with open("config/token.txt", "r") as f:
    TOKEN = f.read()


get_prefix = utils.get_prefix


# Creates the client instance
client = commands.Bot(command_prefix=get_prefix)

# So you can access the functions from cogs
client.get_server_lang = utils.get_server_lang
client.get_server_lang_code = utils.get_server_lang_code

# Setting up connection between Reddit and the bot
with open("config/reddit.json", "r") as f:
    reddit = json.load(f)

client.reddit = praw.Reddit(client_id=reddit["id"],
                            client_secret=reddit["secret"],
                            user_agent='MarzeqsUtilities by u/Marzeq_')

client.__version__ = "0.1.14b"

# Admin command descriptions. It's here because it shouldn't be translated
client.admin_command_descriptions = utils.admin_command_descriptions

# All valid language codes
# client.valid_langs = ["en_US", "es_ES", "pl_PL", "pt_BR", "ru_RU"]
client.valid_langs = ["en_US", "pl_PL"]


# Shows that the bot is working
@client.event
async def on_ready():
    print("The bot is ready.")
    await utils.do_undone_tasks(client)
    if channel_to_send != 0:
        channel = await client.fetch_channel(channel_to_send)
        await channel.send(embed=discord.Embed(title="✅  Restarted the bot", color=0x2be040))


# Basic cog control commands and auto cog loading
# I basically stole this from youtube but it's fine
@client.command(aliases=["l"])
async def load(ctx, extension=None):
    if not await client.is_owner(ctx.author):
        return
    if extension:
        try:
            client.load_extension(f"cogs.{extension}")
            await ctx.message.channel.send(f"Loaded {extension}")
        except commands.errors.ExtensionAlreadyLoaded or commands.errors.ExtensionNotFound:
            await ctx.message.channel.send(f"The cog {extension} is already loaded or does not exist!")
    else:
        for extensionname in os.listdir(f"./cogs"):
            if extensionname.endswith(".py"):
                try:
                    client.load_extension(f"cogs.{extensionname[:-3]}")
                except commands.errors.ExtensionAlreadyLoaded or commands.errors.ExtensionNotFound:
                    pass
        await ctx.message.channel.send(f"Loaded all extensions!")


@client.command(aliases=["ul"])
async def unload(ctx, extension=None):
    if not await client.is_owner(ctx.author):
        return
    if extension:
        try:
            client.unload_extension(f"cogs.{extension}")
            await ctx.message.channel.send(f"Unloaded {extension}")
        except commands.ExtensionNotLoaded or commands.errors.ExtensionNotFound:
            await ctx.message.channel.send(f"The cog {extension} is not loaded or does not exist!")
    else:
        for extensionname in os.listdir(f"./cogs"):
            if extensionname.endswith(".py"):
                try:
                    client.unload_extension(f"cogs.{extensionname[:-3]}")
                except commands.ExtensionNotLoaded or commands.errors.ExtensionNotFound:
                    pass
        await ctx.message.channel.send("Unloaded all extensions!")


@client.command(aliases=["rl"])
async def reload(ctx, extension=None):
    if not await client.is_owner(ctx.author):
        return
    if extension:
        try:
            client.reload_extension(f"cogs.{extension}")
            await ctx.message.channel.send(f"Reloaded {extension}")
        except commands.errors.ExtensionNotFound:
            await ctx.message.channel.send(f"The cog {extension} is not loaded or does not exist!")
    else:
        for extensionname in os.listdir(f"./cogs"):
            if extensionname.endswith(".py"):
                try:
                    client.reload_extension(f"cogs.{extensionname[:-3]}")
                except commands.errors.ExtensionNotFound:
                    pass
        await ctx.message.channel.send("Reloaded all extensions!")


for filename in os.listdir(f"./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")


# Update the internal files from the git repo and rerun the program
@client.command(aliases=["up"])
async def update(ctx):
    if not await client.is_owner(ctx.author):
        return
    await ctx.send(embed=discord.Embed(title="🟡  Pulling from the GitHub repo..", color=0xdaed2d))
    os.system(f"git pull")
    await ctx.send(embed=discord.Embed(title="🟡  Restarting..", color=0xdaed2d))
    os.system(f"{sys.executable} {os.path.dirname(os.path.realpath(__file__))}/main.py {ctx.channel.id}")


@client.command(aliases=["hr"])
async def hardreload(ctx):
    if not await client.is_owner(ctx.author):
        return
    await ctx.send(embed=discord.Embed(title="🟡  Restarting..", color=0xdaed2d))
    os.system(f"{sys.executable} {os.path.dirname(os.path.realpath(__file__))}/main.py {ctx.channel.id}")


client.logger = Logger("log")


# Thanks to mini_bomba for helping me with this part of code
@client.event
async def on_error(name, *args, **_): # noqa
    errorid = round(time.time())
    etype, value, tb = sys.exc_info()
    tb = traceback.TracebackException(type(value), value, tb)
    ready = ["" for _ in range(1000)]
    n = 0
    for line in tb.format():
        if len(ready[n] + line + "\n") > 1024:
            n += 1
        ready[n] += line + "\n"
    ready = [x for x in ready if x != ""]
    embed = discord.Embed(title=f"Error id: `{errorid}`")
    lnenum = 0
    for lne in ready:
        lnenum += 1
        embed.add_field(name=f"Traceback part {lnenum}:", value=f"```{lne}```", inline=False)
    user = await client.fetch_user(500669086947344384)
    await user.send(embed=embed)
    client.logger.critical("".join(ready) + "Error id: " + str(errorid))

client.NoItemFound = utils.NoItemFound

# Run the bot
client.run(TOKEN)

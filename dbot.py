import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands



f = open("token.txt", "r")
TOKEN = f.read()
f.close()

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + '\n')



bot.load_extension("cogs.Events")
bot.load_extension("cogs.Base")
bot.load_extension("cogs.Music")
bot.load_extension("cogs.Funny")
bot.load_extension("cogs.ReVolt")

bot.run(TOKEN)


import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands



f = open("token.txt", "r")
TOKEN = f.read()
f.close()

PREFIX = '/'
random.seed(datetime.now())



TRACKS = [
	["Toys in the Hood 1", "SuperMarket 2", "Museum 2", "Botanical Garden"],
	["Rooftops", "Toy World 1", "Ghost Town 2", "Toy World 2"],
	["Toys in the Hood 2", "Toytanic 1", "Museum 1"],
	["SuperMarket 1", "Ghost Town 2", "Toytanic 2"],
	["Neighborhood Battle", "Garden Battle", "Supermarket Battle", "Museum Battle"],
]

CARS = [
	["RC Bandit", "Dust Mite", "Phat Slug", "Col. Moss", "Harvester", "Dr. Grudge", "Volken Turbo", "Sprinter XL", "BigVolt"],
	["RC San", "Candy Pebbles", "Genghis Kar", "Aqua Sonic", "Mouse", "Mystery", "RC Phink", "LA 54", "Matra XL"],
	["Evil Weasel", "Panga TC", "R6 Turbo", "NY 54", "Bertha Ballistics", "BossVolt", "Shocker", "Splat", "Groovster"],
	["Pest Control", "Adeon", "Pole Poz", "Zipper", "Rotor", "JG-7", "RG1", "RV Loco"],
	["Cougar", "Humma", "Toyeca", "AMW", "Panga", "Probe UFO", "SNW 35", "Purp XL", "Fulon X"],
	["Trolley", "Clockwork Wun", "Clockwork Too", "Clockwork Tree", "Clockwork"],
]



bot = commands.Bot(command_prefix=PREFIX)



@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + '\n')



@bot.command()
async def add(ctx, left : int, right : int):
    """Adds two numbers together."""
    await ctx.send(left + right)

@bot.command()
async def test(ctx):
	await ctx.message.delete()
	mes = await ctx.send("I hope I deleted this^")
	await mes.delete()

@bot.command(aliases = ["playcountryroads"])
async def roads(ctx):
	url = "https://www.youtube.com/watch?v=3qxX5KhCpTk"

	mes = await ctx.send(ctx.message.author.name + " has invoked play country road! PREPARE COMRADES!")
	await play(ctx, url)

	await mes.delete()



#RVGL Commands

@bot.command(name="random_track", aliases = ["rt", "rand_track", "rvrt", "revolt_random_track"])
async def random_track(ctx, level:int=3, upto:bool=True):
	await ctx.message.delete()
	
	track = ""
	mir = ""
	rev = ""

	if(level != 4):
		mir = random.choice(["(M)", ""]);
		rev = random.choice(["(R)", ""]);

	if(upto):
		track = random.choice(random.choice(TRACKS[:level + 1]))
	else:
		track = random.choice(TRACKS[level])
		
	await ctx.send("Random Track: " + track + mir + rev);

@bot.command(name="random_car", aliases = ["rc", "rand_car", "rvrc", "revolt_random_car"])
async def random_car(ctx, level:int=5, upto:bool=True):
	await ctx.message.delete()
	
	car = ""

	if(upto):
		car = random.choice(random.choice(CARS[:level + 1]))
	else:
		car = random.choice(CARS[level]);

	await ctx.send("Random Car: " + car)



bot.load_extension("cogs.Events")
bot.load_extension("cogs.Base")
bot.load_extension("cogs.Music")

bot.run(TOKEN)


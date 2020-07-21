import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import random
from datetime import datetime



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

async def play_callback(voice, headmes, statusmes, name):
	await voice.disconnect()
#	await headmes.delete()
#	await statusmes.delete()
#	print(statusmes)
#	print(name + " has finished playing.")

@bot.event
async def on_ready():
    print('Logged in as ' + bot.user.name + '\n')

@bot.command()
async def hello(ctx):
    """Says world"""
    await ctx.send("world")


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

	

@bot.command(aliases = ["p", "pla"])
async def play(ctx, url:str):
	await ctx.message.delete()
	headmes = await ctx.send(ctx.message.author.name + " has requested " + url + ".")

	statusmes = await ctx.send("Preparing...")
	channel = ctx.message.author.voice.channel
	voice = get(bot.voice_clients, guild=ctx.guild)

	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()
		print(f'Connected to {channel}\n')
	
	song_there = os.path.isfile("song.mp3")
	try:
		if song_there:
			os.remove("song.mp3")
			print("Removed old song file.\n")
	except PermissionError:
		print("Should add song to queue.")
		return
	
	await statusmes.delete()
	statusmes = await ctx.send("Downloading audio...")
	print("Retrieving song.\n")

	voice = get(bot.voice_clients, guild=ctx.guild)

	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		print("Downloading audio now\n")
		ydl.download([url])

	await statusmes.delete()
	statusmes = await ctx.send("Processing...")

	for file in os.listdir("./"):
		if file.endswith(".mp3"):
			name = file
			print(f"Renamed {file} to song.mp3.")
			os.rename(file, "song.mp3")

	await statusmes.delete()
	statusmes = await ctx.send("Playing...")
	voice.play(discord.FFmpegPCMAudio("song.mp3"), after=await play_callback(voice, headmes, statusmes, name))

	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.10



#RVGL Commands

@bot.command(aliases = ["rt", "rvrt", "rvglrt", "rand_track", "random_track"])
async def rv_rand_track(ctx, level:int=3, upto:bool=True):
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

@bot.command(aliases = ["rc", "rvrc", "rvglrc", "rand_car", "random_car"])
async def rv_rand_car(ctx, level:int=5, upto:bool=True):
	await ctx.message.delete()
	
	car = ""

	if(upto):
		car = random.choice(random.choice(CARS[:level + 1]))
	else:
		car = random.choice(CARS[level]);

	await ctx.send("Random Car: " + car)



bot.run(TOKEN)

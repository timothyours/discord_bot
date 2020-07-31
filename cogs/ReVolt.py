from discord.ext import commands

import random
from datetime import datetime



class ReVolt(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.tracks = [
			["Toys in the Hood 1", "SuperMarket 2", "Museum 2", "Botanical Garden"],
			["Rooftops", "Toy World 1", "Ghost Town 2", "Toy World 2"],
			["Toys in the Hood 2", "Toytanic 1", "Museum 1"],
			["SuperMarket 1", "Ghost Town 2", "Toytanic 2"],
			["Neighborhood Battle", "Garden Battle", "Supermarket Battle", "Museum Battle"],
		]

		self.cars = [
			["RC Bandit", "Dust Mite", "Phat Slug", "Col. Moss", "Harvester", "Dr. Grudge", "Volken Turbo", "Sprinter XL", "BigVolt"],
			["RC San", "Candy Pebbles", "Genghis Kar", "Aqua Sonic", "Mouse", "Mystery", "RC Phink", "LA 54", "Matra XL"],
			["Evil Weasel", "Panga TC", "R6 Turbo", "NY 54", "Bertha Ballistics", "BossVolt", "Shocker", "Splat", "Groovster"],
			["Pest Control", "Adeon", "Pole Poz", "Zipper", "Rotor", "JG-7", "RG1", "RV Loco"],
			["Cougar", "Humma", "Toyeca", "AMW", "Panga", "Probe UFO", "SNW 35", "Purp XL", "Fulon X"],
			["Trolley", "Clockwork Wun", "Clockwork Too", "Clockwork Tree", "Clockwork"],
		]
		
		random.seed(datetime.now())

	@commands.command(name="random_track", aliases = ["rt", "rand_track", "rvrt", "revolt_random_track"])
	async def random_track(self, ctx, level:int=3, upto:bool=True):
		await ctx.message.delete()
		
		track = ""
		mir = ""
		rev = ""
	
		if(level != 4):
			mir = random.choice(["(M)", ""]);
			rev = random.choice(["(R)", ""]);
	
		if(upto):
			track = random.choice(random.choice(self.tracks[:level + 1]))
		else:
			track = random.choice(self.tracks[level])
			
		await ctx.send("Random Track: " + track + mir + rev);

	@commands.command(name="random_car", aliases = ["rc", "rand_car", "rvrc", "revolt_random_car"])
	async def random_car(self, ctx, level:int=5, upto:bool=True):
		await ctx.message.delete()
		
		car = ""
	
		if(upto):
			car = random.choice(random.choice(self.cars[:level + 1]))
		else:
			car = random.choice(self.cars[level]);

		await ctx.send("Random Car: " + car)

def setup(bot):
	bot.add_cog(ReVolt(bot));


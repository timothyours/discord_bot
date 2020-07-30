from discord.ext import commands

class Base(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def hello(self, ctx):
		await ctx.send("world")

def setup(bot):
	bot.add_cog(Base(bot));

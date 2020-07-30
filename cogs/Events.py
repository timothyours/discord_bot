from discord.ext import commands

class Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command(self, ctx):
		print("\n" + ctx.message.author.display_name + " invoked command " + ctx.command.name + "\n")

	#@commands.Cog.listener()
	#async def on_command_error(self, ctx, error):
	#	print(ctx.command.name + " was invoked incorrectly.")
	#	print(error)

def setup(bot):
	bot.add_cog(Events(bot))

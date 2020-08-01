import re
from discord.ext import commands



class Events(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command(self, ctx):
		print("\n" + ctx.message.author.display_name + " invoked command " + ctx.command.name + "\n")

	@commands.Cog.listener()
	async def on_message(self, message):
		check = re.findall(r'\/deref', message.content)
		url = re.findall(r'https:\/\/ifunny\.co\/.*?(?:$|\s)', message.content)

		if(not len(check) > 0 and len(url) > 0):
			await self.bot.get_cog("Funny").handle_ifunny(message, url[0])

	#@commands.Cog.listener()
	#async def on_command_error(self, ctx, error):
	#	print(ctx.command.name + " was invoked incorrectly.")
	#	print(error)

def setup(bot):
	bot.add_cog(Events(bot))

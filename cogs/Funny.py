from discord.ext import commands

import requests
from bs4 import BeautifulSoup

class Base(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name="deref")
	async def ifunny_dereference(self, ctx, url):
		await ctx.message.delete()
		r = requests.get(url)
		soup = BeautifulSoup(r.text, "html.parser")

		media = soup.find("div", {"class": "media"})

		if media.has_attr("data-source"):
			src = content=media.attrs["data-source"]
		else:
			src = content=media.find("img").attrs["data-src"]

		await ctx.send(ctx.message.author.display_name + " posted " + src)

def setup(bot):
	bot.add_cog(Base(bot));

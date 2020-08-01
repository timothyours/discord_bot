from discord.ext import commands

import requests
from bs4 import BeautifulSoup

class Funny(commands.Cog):
	def __init__(self, bot):
		self.bot = bot


	async def handle_ifunny(self, message, url):
		await message.delete()
		
		r = requests.get(url)
		soup = BeautifulSoup(r.text, "html.parser")

		media = soup.find("div", {"class": "media"})

		if media.has_attr("data-source"):
			src = content=media.attrs["data-source"]
		else:
			src = content=media.find("img").attrs["data-src"]

		await message.channel.send(message.author.display_name + " posted " + src)


	@commands.command(name="deref")
	async def ifunny_dereference(self, ctx, url):
		"""Takes an iFunny url and gets the direct url for the image or video"""
		
		self.handle_ifunny(ctx.message, url)


def setup(bot):
	bot.add_cog(Funny(bot));

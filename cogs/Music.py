import re
import os
import asyncio
import youtube_dl

import discord
from discord.ext import commands



class Music(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.queue = []
		self.messages = []
		self.current_audio = None
		self.state = None
		self.volume = 0.2

		self.ytdl_opts = {
			'default_search': 'auto',
			'outtmpl': 'music/v_%(id)s.%(ext)s',
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}
		self.ytdl_opts_urls = {
			'outtmpl': 'music/v_%(id)s.%(ext)s',
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}


	
	async def send_message(self, ctx, mes):
		self.messages.append(await ctx.send(mes))

	
	async def pop_message(self):
		await self.messages.pop(len(self.messages) - 1).delete()

	
	async def clear_messages(self):
		while len(self.messages) != 0:
			await self.pop_message()


	async def get_voice(self, channel):
		voice = self.bot.voice_clients
		if not len(voice) == 0:
			voice = voice[0];
		else:
			voice = None

		if voice and voice.is_connected() and not voice.channel.id == channel.id:
			print("Moving to voice channel...")
			await voice[0].move_to(channel)
			print("Done\n")
			return voice[0]
		elif not voice:
			print("Joining voice channel...")
			voice = await channel.connect()
			print("Done\n")

		return voice


	def check_ids(self, i):
		for entry in self.queue:
			if entry["id"] == i:
				print(i + " is in the queue")
				return True
		print(i + " is not in the queue")
		return False


	async def delete_audio(self, i):
		print("Deleting music/v_" + i + ".mp3...")
		os.remove("music/v_" + i + ".mp3")
		print("Done")


	async def purge_audio(self):
		print("Purging audio...")
		for file in os.listdir("./music/"):
			print("Deleting music/" + file + "...")
			os.remove("music/" + file)
		print("Done")


	async def get_audio(self, entry):
		self.messages.append(await entry["chat"].send("Downloading " + entry["title"] + "..."))
		print("Retrieving " + entry["title"] + "...")
		
		with youtube_dl.YoutubeDL(self.ytdl_opts) as ytdl:
			ytdl.download([entry["url"]])

		await self.pop_message()
		print("Done\n")


	async def print_audio(self):
		await self.clear_messages()
		
		mes1 = ""

		if self.state == 0:
			mes1 += "Preparing to play " 
		if self.state == 1:
			mes1 += "Now playing "
		if self.state == 2:
			mes1 += "Paused on "

		mes1 += "**" + self.current_audio["title"] + "**: " + self.current_audio["url"] + "\nRequested by **" + self.current_audio["user"] + "**"

		await self.send_message(self.current_audio["chat"], mes1)

		mes2 = "Queue: "

		if len(self.queue) == 0:
			mes2 += "Empty"
		else:
			mes2 += "[**" + self.queue[0]["title"] + "**"
			if len(self.queue) > 1:
				mes2 += ", **" + self.queue[1]["title"] + "**"
			if len(self.queue) > 2:
				mes2 += ", **" + self.queue[2]["title"] + "**"
			if len(self.queue) > 3:
				mes2 += ", +" + str(len(self.queue) - 3)
			mes2 += "]"

		await self.send_message(self.current_audio["chat"], mes2)



	async def dequeue(self):
		self.current_audio = self.queue.pop(0)

		voice = await self.get_voice(self.current_audio["channel"])


		if self.state == 0:
			self.state = 1
		await self.print_audio()

		def play_callback(err):
			if len(self.queue) > 0:
				print("HERE: ", end="")
				print(self.check_ids(self.current_audio["id"]))
				if not self.check_ids(self.current_audio["id"]):
					asyncio.run_coroutine_threadsafe(self.delete_audio(self.current_audio["id"]), self.bot.loop)
				asyncio.run_coroutine_threadsafe(self.dequeue(), self.bot.loop)
			else:
				self.current_audio = None
				asyncio.run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
				asyncio.run_coroutine_threadsafe(self.clear_messages(), self.bot.loop)
				asyncio.run_coroutine_threadsafe(self.purge_audio(), self.bot.loop)

		voice.play(discord.FFmpegPCMAudio("music/v_" + self.current_audio["id"] + ".mp3"), after=play_callback)
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = self.volume
		
		if self.state == 2:
			voice.pause()


	#Gets video information and adds it to the queue
	async def enqueue(self, ctx, search):
		entry = None

		with youtube_dl.YoutubeDL(self.ytdl_opts) as ytdl:
			info = ytdl.extract_info(search, download=False)
		
			if re.match(r'https:\/\/www\.youtube\.com\/.*', search):
				entry = {
					"user": ctx.message.author.display_name,
					"channel": ctx.author.voice.channel,
					"title": info["title"],
					"url": search,
					"chat": ctx,
					"id": info["id"],
				}
			else:
				entry = {
					"user": ctx.message.author.display_name,
					"channel": ctx.author.voice.channel,
					"title": info["entries"][0]["title"],
					"url": info["entries"][0]["webpage_url"],
					"chat": ctx,
					"id": info["entries"][0]["id"],
				}
		
		if self.current_audio is None:
			print("Preparing to play " + entry["title"] + ": " + entry["url"])
			self.state = 0
			#await self.print_audio()
		
		if not self.check_ids(entry["id"]) and (self.current_audio is None or entry["id"] != self.current_audio["id"]):
			await self.get_audio(entry)

		self.queue.append(entry)



	@commands.command(name="pause", aliases=["pawse"])
	async def pause(self, ctx):
		"""Pauses music"""

		await ctx.message.delete()
		
		print("Pausing audio...")

		voice = ctx.guild.voice_client
		if voice.is_playing:
			voice.pause()

		self.state = 2
		await self.print_audio()

		print("Done")


	@commands.command(name="resume", aliases=["unpause", "start"])
	async def resume(self, ctx):
		"""Resumes music"""

		await ctx.message.delete()
		
		print("Playing audio...")

		voice = ctx.guild.voice_client
		if voice.is_paused():
			voice.resume()

		self.state = 1
		await self.print_audio()

		print("Done")


	@commands.command(name="stop")
	async def stop(self, ctx):
		"""Stops music"""

		await ctx.message.delete()

		print("Stopping audio")

		voice = ctx.guild.voice_client
		if voice:
			self.current_audio = None
			self.queue.clear()
			voice.stop()

		self.state = 0
		await self.clear_messages()

		print("Done")

	
	@commands.command(name="skip")
	async def skip(self, ctx):
		"""Skips current song"""

		await ctx.message.delete()

		print("Skipping audio")

		voice = ctx.guild.voice_client
		if voice:
			voice.stop()

		print("Done")


	@commands.command(aliases = ["enqueue", "queue"])
	async def play(self, ctx, *args):
		"""Plays music from YouTube"""
		
		await ctx.message.delete()

		search = ' '.join(args)

		await self.enqueue(ctx, search)
		print(self.queue[-1]["user"] + " added " + self.queue[-1]["title"] + " to the queue")

		if(self.current_audio is None):
			await self.dequeue()
		else:
			await self.print_audio()
	

	@commands.command(hidden = True)
	async def moan(self, ctx):
		"""Moan"""

		await ctx.message.delete()
		
		voice = await self.get_voice(ctx.author.voice.channel)

		def play_callback(err):
			if len(self.queue) > 0:
				asyncio.run_coroutine_threadsafe(self.dequeue(), self.bot.loop)
			else:
				self.current_audio = None
				asyncio.run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
				asyncio.run_coroutine_threadsafe(self.clear_messages(), self.bot.loop)

		voice.play(discord.FFmpegPCMAudio("moan.mp3"), after=play_callback)
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = self.volume



def setup(bot):
	bot.add_cog(Music(bot))


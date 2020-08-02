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

		self.ytdl_opts = {
			'default_search': 'auto',
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3',
				'preferredquality': '192',
			}],
		}
		self.ytdl_opts_urls = {
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


	async def get_audio(self, url):
		song_there = os.path.isfile("song.mp3")
		try:
			if song_there:
				os.remove("song.mp3")
				print("Removed old song file\n")
		except PermissionError:
			print("Should add song to queue.")
			return


		self.messages.append(await self.current_audio["chat"].send("Downloading audio..."))
		print("Retrieving audio")
		
		with youtube_dl.YoutubeDL(self.ytdl_opts) as ytdl:
			print("Downloading audio now")
			ytdl.download([url])

		await self.pop_message()
		print("Done\n")


		self.messages.append(await self.current_audio["chat"].send("Processing..."))
		print("Rearranging files...")
	
		for file in os.listdir("./"):
			if file.endswith(".mp3"):
				name = file
				print(f"Renamed {file} to song.mp3.")
				os.rename(file, "song.mp3")

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

		print("Preparing to play " + self.current_audio["title"] + ": " + self.current_audio["url"])

		prev = self.state
		self.state = 0
		await self.print_audio()

		await self.get_audio(self.current_audio["url"])

		if prev == 0:
			self.state = 1
		else:
			self.state = prev
		await self.print_audio()

		def play_callback(err):
			if len(self.queue) > 0:
				asyncio.run_coroutine_threadsafe(self.dequeue(), self.bot.loop)
			else:
				self.current_audio = None
				asyncio.run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)
				asyncio.run_coroutine_threadsafe(self.clear_messages(), self.bot.loop)

		voice.play(discord.FFmpegPCMAudio("song.mp3"), after=play_callback)
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = 0.1
		
		if self.state == 2:
			voice.pause()


	#Gets video information and adds it to the queue
	async def enqueue(self, ctx, search):
		with youtube_dl.YoutubeDL(self.ytdl_opts) as ytdl:
			info = ytdl.extract_info(search, download=False)
		
			if re.match(r'https:\/\/www\.youtube\.com\/.*', search):
				self.queue.append({
					"user": ctx.message.author.display_name,
					"channel": ctx.author.voice.channel,
					"title": info["title"],
					"url": search,
					"chat": ctx,
				})
			else:
				self.queue.append({
					"user": ctx.message.author.display_name,
					"channel": ctx.author.voice.channel,
					"title": info["entries"][0]["title"],
					"url": info["entries"][0]["webpage_url"],
					"chat": ctx,
				})



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



def setup(bot):
	bot.add_cog(Music(bot))


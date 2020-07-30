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

		self.ytdl_opts = {
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


	async def join(self, ctx):
		destination = ctx.author.voice.channel
		voice = ctx.guild.voice_client
	
		if voice:
			await voice.move_to(destination)
			return voice
	
		voice = await destination.connect()
		return voice


	async def get_audio(self, ctx, url):
		song_there = os.path.isfile("song.mp3")
		try:
			if song_there:
				os.remove("song.mp3")
				print("Removed old song file\n")
		except PermissionError:
			print("Should add song to queue.")
			return


		self.messages.append(await ctx.send("Downloading audio..."))
		print("Retrieving audio")
	
		with youtube_dl.YoutubeDL(self.ytdl_opts) as ytdl:
			print("Downloading audio now")
			ytdl.download([url])

		await self.pop_message()
		print("Done\n")


		self.messages.append(await ctx.send("Processing..."))
		print("Rearranging files...")
	
		for file in os.listdir("./"):
			if file.endswith(".mp3"):
				name = file
				print(f"Renamed {file} to song.mp3.")
				os.rename(file, "song.mp3")

		await self.pop_message()
		print("Done\n")


	async def dequeue(self, ctx):
		while len(self.messages) != 0:
			self.pop_message

		voice = ctx.guild.voice_client
		url = self.queue.pop(0)
		print("Preparing to play " + url)
		
		await self.send_message(ctx, "Preparing to play " + url)
		await self.get_audio(ctx, url)
		await self.pop_message()
		await self.send_message(ctx, "Now playing " + url + "\nRequested by " + ctx.message.author.display_name)
		
		def play_callback(err):
			asyncio.run_coroutine_threadsafe(self.pop_message(), self.bot.loop)

			if len(self.queue) > 0:
				asyncio.run_coroutine_threadsafe(self.dequeue(ctx), self.bot.loop)
			else:
				asyncio.run_coroutine_threadsafe(voice.disconnect(), self.bot.loop)


		voice.play(discord.FFmpegPCMAudio("song.mp3"), after=play_callback)
		
		voice.source = discord.PCMVolumeTransformer(voice.source)
		voice.source.volume = 0.1



	@commands.command(name="pause", aliases=["pawse"])
	async def pause(self, ctx):
		"""Pauses music"""

		await ctx.message.delete()
		
		voice = ctx.guild.voice_client
		if voice.is_playing:
			voice.pause()


	@commands.command(name="start", aliases=["unpause", "resume"])
	async def start(self, ctx):
		"""Resumes music"""

		await ctx.message.delete()
		
		voice = ctx.guild.voice_client
		if voice.is_paused():
			voice.resume()


	@commands.command(name="stop")
	async def stop(self, ctx):
		"""Stops music"""

		await ctx.message.delete()

		voice = ctx.guild.voice_client
		if voice:
			self.queue.clear()
			voice.stop()

	
	@commands.command(name="skip")
	async def skip(self, ctx):
		"""Skips current song"""

		await ctx.message.delete()

		voice = ctx.guild.voice_client
		if voice:
			voice.stop()


	@commands.command(aliases = ["enqueue", "queue"])
	async def play(self, ctx, url:str, count=1):
		"""Plays music from YouTube"""
		
		await ctx.message.delete()

		self.queue.append(url)
		print(ctx.message.author.display_name + " added " + url + " to the queue")

		voice = ctx.guild.voice_client

		if voice and voice.is_playing():
			return

		
		print("Joining voice channel...")
		if not voice:
			voice = await self.join(ctx)
		print("Done\n")

		await self.dequeue(ctx)



def setup(bot):
	bot.add_cog(Music(bot))


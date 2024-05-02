# music.py (inside 'cogs' folder)
import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

    intents = discord.Intents.default()

    intents.members = True

    async def play_next(self, ctx):
        if self.queues[ctx.guild.id] != []:
            # Fetch the first song in the queue
            link = self.queues[ctx.guild.id].pop(0)
            await self.play(ctx, link)
    
    @commands.command()
    async def play(self, ctx, link):
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:
            loop = asyncio.get_event_loop()
            data = await asyncio.get_event_loop().run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)
            self.voice_clients[ctx.guild.id].play(player, after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send("กำลังเล่นเพลง...")

        except Exception as e:
            print(e)

    @commands.command(name = "clearqueue")
    async def clear_queue(self, ctx):
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send("เคลียคิวแล้ว")
        else:
            await ctx.send("ไม่มีคิว")

    @commands.command()
    async def skip(self, ctx):
        try:
            # Stop the currently playing song
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)  # Play the next song in the queue
            await ctx.send("ข้ามเพลงแล้ว...")
        except Exception as e:
            print(e)


    @commands.command()
    async def pause(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].pause()
            await ctx.send("หยุดเพลงชั่วคราว...")
        except Exception as e:
            print(e)

    @commands.command()
    async def resume(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].resume()
            await ctx.send("เล่นเพลงต่อ...")
        except Exception as e:
            print(e)

    @commands.command()
    async def stop(self, ctx):
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send("หยุดเล่นเพลงแล้ว...")
        except Exception as e:
            print(e)
            
    @commands.command()
    async def queue(self, ctx, url):
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(url)
        await ctx.send("เพิ่มเข้าคิวแล้ว...")
            
async def setup(bot):
    await bot.add_cog(Music(bot))
    
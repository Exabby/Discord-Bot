# music.py (inside 'cogs' folder)
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp
from yt_dlp import YoutubeDL
import asyncio

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queues = {}
        self.voice_clients = {}
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}

    intents = discord.Intents.default()

    intents.members = True

    music_channel_id = None

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def music_ch(self, ctx, *, id: str):
        print("id = "+ id)
        if id.startswith('"') and id.endswith('"'):
            self.music_channel_id = int(id.strip('"'))
            channel = self.client.get_channel(self.music_channel_id)
        
            await ctx.send(f">>> ต่อไปนี้คำสั่งเพลงจะใช้ได้เฉพาะในห้องนี้นะ {channel.mention}")
        else:
            await ctx.send(">>> ให้ใส่ ID ห้องในเครื่องหมายคำพูด \"\" ")
    
    
    async def play_next(self, ctx):
        if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
            # Fetch the first song in the queue
            link = self.queues[ctx.guild.id].pop(0)
            await self.play(ctx, link=link)
        else:
            await ctx.send(">>> หมดเพลงจะเล่นแล้ว ออกห้องมาแล้วจ้า...")
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]


    @commands.command()
    async def play(self, ctx, *, link):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        if ctx.guild.id in self.voice_clients and ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        if ctx.guild.id in self.voice_clients and self.voice_clients[ctx.guild.id].is_playing():
            await ctx.send(">>> เพลงกำลังเล่นอยู่นะ ถ้าต้องการเพิ่มเพลงเข้าคิว ให้ใช้คำสั่ง queue")
            return
        try:
            voice_client = await ctx.author.voice.channel.connect()
            self.voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        try:
            loop = asyncio.get_event_loop()

            # Check if link is a URL or a song name
            if not link.startswith('http'):
                videosSearch = VideosSearch(link, limit = 1)
                
                result = videosSearch.result()
                if isinstance(result, dict) and 'result' in result:
                    first_result = result['result'][0]
                    link = first_result['link']
                else:
                    await ctx.send(">>> หาเพลงไม่เจอ...")
                    return

            data = await asyncio.get_event_loop().run_in_executor(None, lambda: self.ytdl.extract_info(link, download=False))
            song = data['url']
            player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)
            self.voice_clients[ctx.guild.id].play(player, after=lambda e: self.client.loop.create_task(self.play_next(ctx)))
            title = data.get('title', 'Unknown')
            duration = data.get('duration', 0)
            minutes, seconds = divmod(duration, 60)
            await ctx.send(f">>> กำลังเล่นเพลง {title} ความยาว {minutes}:{seconds:02d}")

        except Exception as e:
            print(e)

    @commands.command(name = "clearqueue")
    async def clear_queue(self, ctx):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
            await ctx.send(">>> เคลียคิวแล้ว")
        else:
            await ctx.send(">>> ไม่มีคิว")

    @commands.command()
    async def skip(self, ctx):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        try:
            self.voice_clients[ctx.guild.id].stop()
            await ctx.send(">>> ข้ามไปเพลงถัดไปแล้ว...")
        except Exception as e:
            print(e)


    @commands.command()
    async def pause(self, ctx):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        try:
            self.voice_clients[ctx.guild.id].pause()
            await ctx.send(">>> หยุดเพลงชั่วคราว...")
        except Exception as e:
            print(e)

    @commands.command()
    async def resume(self, ctx):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        try:
            self.voice_clients[ctx.guild.id].resume()
            await ctx.send(">>> เล่นเพลงต่อ...")
        except Exception as e:
            print(e)

    @commands.command()
    async def stop(self, ctx):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            await ctx.send(">>> หยุดเล่นเพลงแล้ว...")
        except Exception as e:
            print(e)
            
    @commands.command()
    async def queue(self, ctx, *, link):
        if self.music_channel_id and ctx.channel.id != self.music_channel_id:
            return
        if ctx.author.voice is None or ctx.author.voice.channel != self.voice_clients[ctx.guild.id].channel:
            await ctx.send(">>> ต้องอยู่ในห้องเดียวกันกับบอทนะถึงจะใช้คำสั่งเพลงได้...")
            return
        if not link.startswith('http'):
            videosSearch = VideosSearch(link, limit = 1)
            result = videosSearch.result()
            if isinstance(result, dict) and 'result' in result:
                first_result = result['result'][0]
                link = first_result['link']
            else:
                await ctx.send(">>> หาเพลงไม่เจอ...")
                return

        # Add the song to the queue
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(link)
        await ctx.send(">>> เพิ่มเพลงเข้าคิวแล้ว...")
            
async def setup(client):
    await client.add_cog(Music(client))
    

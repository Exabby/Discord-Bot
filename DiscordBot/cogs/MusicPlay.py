# music.py (inside 'cogs' folder)
import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
import yt_dlp
from yt_dlp import YoutubeDL
import asyncio
import json
from utils import utils

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client  # The discord client
        self.queues = {}  # A dictionary to hold the music queues for each guild
        self.voice_clients = {}  # A dictionary to hold the voice clients for each guild
        self.yt_dl_options = {"format": "bestaudio/best"}  # Options for the YoutubeDL instance
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)  # The YoutubeDL instance
        self.ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -filter:a "volume=0.25"'}  # Options for ffmpeg
        self.ids = utils.load_ids() # Load the ids from the ids.json file
        self.music_channel_id = self.ids.get('music_channel_id')  
        self.playskip_used = False  # A flag to check if the playskip command was used
        self.looping = {}  # A dictionary to keep track of looping for each guild
        self.current_song = {}  # A dictionary to keep track of the current song for each guild


    # I don't know what is this, but somehow I need it
    intents = discord.Intents.default()
    intents.members = True

    
            
    # Save the ids to the ids.json file
    def save_ids(self):
        self.ids['music_channel_id'] = self.music_channel_id
        utils.save_ids(self.ids)
            
    # A command to set the music channel
    @commands.command(name="music")
    @commands.has_permissions(administrator=True)
    async def musicSetting(self, ctx, id: str):
        try:
            self.music_channel_id = int(id)
            self.save_ids()

            channel = self.client.get_channel(self.music_channel_id)
            if channel is None:
                await ctx.send(">>> ไม่พบห้องที่ระบุ โปรดตรวจสอบ ID อีกครั้ง")
                return

            await ctx.send(f">>> ต่อไปนี้คำสั่งเพลงจะใช้ได้เฉพาะในห้องนี้นะ {channel.mention}")
        except ValueError:
            await ctx.send(">>> ID ของห้องไม่ถูกต้อง โปรดระบุ ID ที่เป็นตัวเลข")
        except Exception as e:
            await ctx.send(f">>> บอทหลอน ไปเช็คคอนโซล")
            print(f"Error in musicSetting command: {e}")
    
    # A function to play the next song in the queue
    async def play_next(self, ctx):
        if self.looping.get(ctx.guild.id, False):  # If looping is enabled for this guild
            await self.play(ctx, link=self.current_song[ctx.guild.id])  # Play the current song again
        else:
            if ctx.guild.id in self.queues and self.queues[ctx.guild.id]:
                    # Fetch the first song in the queue
                link = self.queues[ctx.guild.id].pop(0)
                await self.play(ctx, link=link)
            else:
                if not self.playskip_used:  # Only disconnect if the playskip command was not used
                    await ctx.send(">>> หมดเพลงจะเล่นแล้ว ออกห้องมาแล้วจ้า...")
                    await self.voice_clients[ctx.guild.id].disconnect()
                    del self.voice_clients[ctx.guild.id]
                self.playskip_used = False
        

    # A command to play a song
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
        if ctx.guild.id not in self.current_song:
                self.current_song[ctx.guild.id] = None

        self.current_song[ctx.guild.id] = link  # Store the current song

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

    # A command to clear the music queue
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
    # A command to skip the current song
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

    # A command to pause the current song
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
    # A command to resume the current song
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

    # A command to stop the current song
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
        
    # A command to add a song to the queue
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
    
    # A command to play a mext requested song immedietly    
    @commands.command()
    async def playskip(self, ctx, *, link):
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
            
        self.voice_clients[ctx.guild.id].stop()
        self.queues[ctx.guild.id] = []
        self.playskip_used = True
        await self.play(ctx, link=link)
        await ctx.send(">>> ข้ามเพลงแล้ว กำลังเล่นเพลงใหม่...")
    
    # A command to loop the current song
    @commands.command()
    async def loop(self, ctx):
        if ctx.guild.id not in self.looping:
            self.looping[ctx.guild.id] = False

        self.looping[ctx.guild.id] = not self.looping[ctx.guild.id]  # Toggle looping
        if self.looping[ctx.guild.id]:
            await ctx.send(">>> วนซ้ำเพลงปัจจุบัน.")
        else:
            await ctx.send(">>> ปิดการวนซ้ำเพลงปัจจุบัน.")
    
async def setup(client):
    await client.add_cog(Music(client))
    

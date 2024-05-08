import discord
from discord.ext import commands
from apikeys import *
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from discord.ext import commands
class PlayFile(commands.Cog):
    
    music_queues = {}
    def __init__(self, client):
        self.client = client
    
    intents = discord.Intents.default()

    intents.members = True


    def check_queue(self, ctx, id):
        if self.music_queues[id] != []:
            voice = ctx.guild.voice_client
            source = self.music_queues[id].pop(0)
            player = voice.play(source)
            
    @commands.command(pass_context=True)
    async def join(self, ctx):
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        else:
            await ctx.send("พี่ไม่ได้อยู่ในห้อง ใช้คำสั่งนี้ไม่ได้นะ")

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        if(ctx.voice_client):
            await ctx.guild.voice_client.disconnect()
            await ctx.send("ไกปู ออกจาห้องมาละ")
        else:
            await ctx.send("ผมไม่ได้อยู่ในห้องครับพี่")
            
    @commands.command(pass_context = True)
    async def pauseFile(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        if voice.is_playing():
            voice.pause()
            await ctx.send("หยุดเพลงชั่วคราว...")
        else:
            await ctx.send("ยังไม่ได้เล่นไร")

    @commands.command(pass_context = True)
    async def resumeFile(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        if voice.is_paused():
            voice.resume()
            await ctx.send("เล่นเพลงต่อ...")
        else:
            await ctx.send("เพลงมันก็เล่นอยู่ จะเล่นซ้ำหาไรอะ")

    @commands.command(pass_context = True)
    async def stopFile(self, ctx):
        voice = discord.utils.get(self.client.voice_clients, guild = ctx.guild)
        voice.stop()
        await ctx.send("หยุดเล่นเพลง...")
    # -------------- Join VC and Leave -------------->
    # ---------------- Play Music
    @commands.command(pass_context = True)
    async def playfile(self, ctx, arg):
        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await ctx.send("พี่ไม่ได้อยู่ในห้อง เล่นไม่ได้")
            return

        voice_channel = ctx.author.voice.channel
        voice = ctx.guild.voice_client

        if voice and voice.is_connected():
            await voice.move_to(voice_channel)
        else:
            voice = await voice_channel.connect()

        audio_file_name = "audio/" + str(arg) + ".mp3"
        source = FFmpegPCMAudio(audio_file_name)
        player = voice.play(source, after=lambda x=None: self.check_queue(ctx, ctx.message.guild.id))

        await ctx.send("กำลังเล่น " + str(arg) + "...")
        
    @commands.command(pass_context = True)
    async def queueFile(self, ctx, arg):
        voice = ctx.guild.voice_client
        audio_file_name = "audio/" + str(arg) + ".mp3"
        source = FFmpegPCMAudio(audio_file_name)
        
        guild_id = ctx.message.guild.id
        
        if guild_id in self.music_queues:
            self.music_queues[guild_id.append(source)]
        else:
            self.music_queues[guild_id] = [source]
            
        await ctx.send("เพิ่มเข้าคิวแล้ว")

# async def setup(client):
#     await client.add_cog(PlayFile(client))

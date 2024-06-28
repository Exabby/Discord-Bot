import asyncio
import discord
from discord.ext import commands
from tools.timeoutHandler import msgCheckTimeoutApply 

class MsgCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout_duration = 10 # Timeout duration in seconds
        self.words = ["กามู", "ไกปู", "มา"] # Forbidden words
        
    @commands.command(name="addWord")
    @commands.has_permissions(administrator=True)
    async def add_word(self, ctx, *, message):
        self.words.append(message)
        await ctx.send(f">>> เพิ่มอันนี้เข้าไปในคลังคำห้ามใช้แล้ว: {message}")
    
    @commands.command(name="removeWord")
    @commands.has_permissions(administrator=True)
    async def remove_word(self, ctx, *, message):
        if message in self.words:
            self.words.remove(message)
            await ctx.send(f">>> ลบอันนี้ออกจากคลังคำห้ามใช้แล้ว: {message}")
        else:
            await ctx.send(f">>> ไม่พบคำนี้ในคลังคำห้ามใช้: {message}")
    
    @commands.command(name="wordList")
    async def word_list(self, ctx):
        word_string = ", ".join(self.words)
        await ctx.send(f">>> คำที่อยู่ในคลังคำห้ามใช้: [{word_string}]")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.author == self.bot.user:
                return  # Ignore messages from the bot itself
            
            # Check if the message content contains any forbidden words
            if message.content in self.words:
            
                if message.author.top_role > message.guild.me.top_role:
                    await message.channel.send(">>> " + message.content + " อะไ- ขอโทษครับพี่ ลืมดูคนพิมพ์")
                    return
                
                await message.channel.send(">>> " + message.content + " ไร เอาไป " + str(self.timeout_duration) + " วิ")
            
                await msgCheckTimeoutApply(message, self.timeout_duration)
        except Exception as e:
            print(e)
            await message.channel.send(e)
        
async def setup(bot):
    await bot.add_cog(MsgCheck(bot))

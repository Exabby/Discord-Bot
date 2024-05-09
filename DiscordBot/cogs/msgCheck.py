import asyncio
import discord
from discord.ext import commands

class MsgCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout_duration = 10

        self.words = ["กามู","ไกปู","มา"]
        
    @commands.command(name="addWord" )
    @commands.has_permissions(administrator=True)
    async def add_word(self, ctx, *, message):
        self.words.append(message)
        await ctx.send(f">>> เพิ่มอันนี้เข้าไปในคลังคำห้ามใช้แล้ว: {message}")
    
    @commands.command(name="removeWord" )
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
        # Check if the message content meets your criteria
        if message.content in self.words:
            if message.author.top_role > message.guild.me.top_role:
                await message.channel.send(">>> "+ message.content +"อะไ- ขอโทษครับพี่ ลืมดูคนพิมพ์")
                return
            
            # Perform some action or send a response
            await message.channel.send(">>> "+message.content + "ไร เอาไป " + str(self.timeout_duration) + " วิ")

            # Define a role for timeout
            timeout_role = discord.utils.get(">>> "+ message.guild.roles, name="Timeout")

            # Store the member's current roles
            current_roles = message.author.roles
            
            # Remove all roles from the member
            for role in current_roles:
                if role != message.guild.default_role:  # Don't remove the default role
                    await message.author.remove_roles(role)
            
            # Add the role to the member
            await message.author.add_roles(timeout_role)

            # Wait for the duration of the timeout, then remove the role
            await asyncio.sleep(self.timeout_duration)
            
            await message.author.remove_roles(timeout_role)

             # Add the original roles back to the member
            for role in current_roles:
                if role != message.guild.default_role:  # Don't add the default role
                    await message.author.add_roles(role)
            
async def setup(bot):
    await bot.add_cog(MsgCheck(bot))
import asyncio
import discord
from discord.ext import commands

class MsgCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timeout_duration = 10

        self.words = ["กามู","ไกปู"]
    @commands.Cog.listener()
    async def on_message(self, message):
        # Check if the message content meets your criteria
        if message.content in self.words:
            if message.author.top_role > message.guild.me.top_role:
                await message.channel.send( message.content +"อะไ- ขอโทษครับพี่ ลืมดูคนพิมพ์")
                return
            
            # Perform some action or send a response
            await message.channel.send(message.content + "ไร เอาไป " + str(self.timeout_duration) + " วิ")

            # Define a role for timeout
            timeout_role = discord.utils.get(message.guild.roles, name="Timeout")

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
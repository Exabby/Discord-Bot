import discord
from discord.ext import commands
import asyncio

class Echo(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.target_channel = None
        self.client.loop.create_task(self.send_console_messages())

    @commands.command()
    async def setchannel(self, ctx, channel: discord.TextChannel):
        self.target_channel = channel
        await ctx.send(f'เซ็ทห้องละจา : {channel.mention}')

    async def send_console_messages(self):
        await self.client.wait_until_ready()
        while not self.client.is_closed():
            console_input = await self.client.loop.run_in_executor(None, input, "> ")
            if self.target_channel:
                await self.target_channel.send(console_input)
            else:
                print("Target channel is not set. Use the setchannel command to set it.")

async def setup(client):
    await client.add_cog(Echo(client))

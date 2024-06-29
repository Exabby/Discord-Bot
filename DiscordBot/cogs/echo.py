import discord
from discord.ext import commands
import asyncio
from utils import utils 


class Echo(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.ids = utils.load_ids()
        
        self.client.loop.create_task(self.send_console_messages())

    def save_ids(self):
        self.ids['chatChannel_id'] = self.chatChannel_id
        utils.save_ids(self.ids)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.chatChannel_id = self.ids.get('chatChannel_id')      
        self.target_channel = self.client.get_channel(self.chatChannel_id) if self.chatChannel_id else None
    
    @commands.command(name="setChannel")
    async def setchannel(self, ctx, channel: discord.TextChannel):
        try:
            self.target_channel = channel
            self.chatChannel_id = channel.id
            self.save_ids()
            await ctx.send(f'เซ็ทห้องละจา : {channel.mention}')
        except Exception as e:
            print(e)
            await ctx.send(e)
    
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

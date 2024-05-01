import discord
from discord.ext import commands

class MyCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("-----")
        
    # @commands.command()
    # async def ping(self, ctx):
    
    # @commands.Cog.listener()
    # async def on_ready(self):

async def setup(client):
    await client.add_cog(MyCog(client))

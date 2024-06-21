import discord
from discord.ext import commands, tasks
from itertools import cycle
from apikeys import *
import os
import asyncio

client = commands.Bot(command_prefix="gd ", intents=discord.Intents.all())
bot_status = cycle(["Type 'gd' prefix for command", "พิมพ์ gd เพื่อใช้คำสั่ง"])

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))


@client.event
async def on_ready():
    print("-----------------------")
    print("Bot is Online...\n-----------------------")
    change_status.start()

async def load_cogs():
    print("-----------------------")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await client.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded extension: {filename}")
            except Exception as e:
                print(f"Failed to load extension {filename}: {e}")



async def main():
    async with client:
        await load_cogs()
        await client.start(BOTTOKEN)

        
asyncio.run(main())


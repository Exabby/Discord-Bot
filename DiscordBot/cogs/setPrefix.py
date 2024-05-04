import discord
from discord.ext import commands

MAX_PREFIX_LENGTH = 5

class setPrefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="prefix", description="Set a new command prefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, *, new_prefix: str):
        if new_prefix.startswith('"') and new_prefix.endswith('"'):
            new_prefix = new_prefix[1:-1]
            
            if len(new_prefix) > MAX_PREFIX_LENGTH:
                await ctx.send(f">>> ยาวไป ขอไม่เกิน {MAX_PREFIX_LENGTH} ตัว รวมเว้นวรรค")
                return

            self.client.command_prefix = new_prefix
            await ctx.send(f">>> ต่อไปนี้ให้ใช้อันนี้แทนนะ :  `{new_prefix}`")
        else:
            await ctx.send(">>> ให้ใส่ prefix ใหม่ในเครื่องหมายคำพูดตัวนี้นะ \" \" ")

async def setup(client):
    await client.add_cog(setPrefix(client))

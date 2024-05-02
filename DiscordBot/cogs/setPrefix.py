import discord
from discord.ext import commands

class setPrefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="prefix", description="Set a new command prefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, new_prefix: str):
        if len(new_prefix) > 5:
            await ctx.send("ยาวไป ขอไม่เกิน 2 ตัว")
            return

        self.client.command_prefix = new_prefix+" "
        await ctx.send(f"ต่อไปนี้ให้ใช้อันนี้แทนนะ :  `{new_prefix}`")

    @set_prefix.error
    async def set_prefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("คุณไม่มีสิทธีใช้คำสั่งนี้")

async def setup(client):
    await client.add_cog(setPrefix(client))
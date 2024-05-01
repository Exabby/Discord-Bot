import discord
from discord.ext import commands


class SelfRoles(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Dogta2", style=discord.ButtonStyle.success, emoji="<:dota2:1199758271599349780>")
    async def get_role(self, interaction: discord.Interaction, Button: discord.ui.Button):
        test_role = discord.utils.get(interaction.guild.roles, id=1235153789380595786)
        
        if test_role in interaction.user.roles:
            await interaction.user.remove_roles(test_role)
            await interaction.response.send_message(content="ถอดยศหมาแล้วครับ", ephemeral=True)
        else:
            await interaction.user.add_roles(test_role)
            await interaction.response.send_message(content="ให้ยศหมา ๆ แล้วครับ", ephemeral=True)


class getRole(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    @commands.command(name="selfrole", description="รับยศ")
    async def self_role(sefl, ctx):
        await ctx.send("กดปุ่มเพื่อรับ/ถอดยศ Dogta2", view=SelfRoles())

async def setup(client):
    await client.add_cog(getRole(client))

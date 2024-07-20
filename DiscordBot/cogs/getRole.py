import json
import discord
from discord.ext import commands
from utils import utils 


buttonPath = "data/roleButton.json"

class Role(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        try:
            with open(buttonPath, "r") as f:
                buttons = json.load(f)
        except Exception as error:
            print("An exception occurred:", error)
        
        try:
            for button in buttons:
                self.add_item(RoleButton(
                    label=button["label"],
                    style=getattr(discord.ButtonStyle, button["style"]),
                    emoji=button["emoji"],
                    role_id=button["role_id"]
                ))

        except Exception as error:
            print("An exception occurred:", error)
        
class RoleButton(discord.ui.Button):
    def __init__(self, label, style, emoji, role_id):
        super().__init__(label=label, style=style, emoji=emoji)
        self.role_id = role_id
    
    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, id=self.role_id)
        await interaction.user.add_roles(role)
        await interaction.response.send_message(content="ให้ยศเออแล้วจา", ephemeral=True)

class getRole(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        self.ids = utils.load_ids()
        self.roleChannelId = self.ids.get('roleChannel_id')
        self.title = "รับยศเออ"
        self.description = "ไม่รับก็พูดไม่ได้อะ เออ"
        self.url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCQH_Iwy3xbLNb4f2FeNz01tTuhIUwuV5yFfCpINvItA&s"
        self.btnEmoji = "<:huckmon:1252909075776278579>"
        self.btnStyle = "primary"
        self.btnName = "เออ"
        
    async def clear_channel(self, channel_id):
        channel = self.client.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):  # Ensure it's a text channel
            try:
                await channel.purge(limit=None)
            except Exception as e:
                print(f"Failed to clear channel {channel_id}: {e}")
        else:
            print(f"Channel with ID {channel_id} not found or not a text channel.")
    
    async def gameRoleEmbed(self, ctx = None, roleChannelId = None):
        try:
                embed = discord.Embed(
                    title="**รับยศเออ**",
                    description=f"ไม่รับก็พูดไม่ได้อะ เออ",
                    color=0xB2BEB5
                )
                embed.set_image(url="https://cdn.discordapp.com/icons/869618577106427974/a_acec8db6bb8253faf458f8cd544fe9a2.gif?size=128")
                
                if roleChannelId:
                    channel = self.client.get_channel(roleChannelId)
                    if isinstance(channel, discord.TextChannel):  # Ensure the channel is a text channel
                        await channel.send(embed=embed, view=Role())
                    else:
                        print(f"Channel with ID {roleChannelId} not found or not a text channel.")
                #     return

                if ctx:
                    # Send the embed with buttons
                    message = await ctx.send(embed=embed, view=Role())
                    # Delete the command message
                    await ctx.message.delete()
                
        except Exception as e:
            print(e)
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            await self.clear_channel(self.roleChannelId)
            await self.gameRoleEmbed(roleChannelId=self.roleChannelId)
            print(self.roleChannelId)
        except Exception as e:
            print(e)
    
    # @commands.command(name="role", description="รับยศ")
    # async def role(self, ctx):
    #     if ctx.author.guild_permissions.administrator:
    #         await self.gameRoleEmbed(ctx)
        
async def setup(client):
    await client.add_cog(getRole(client))

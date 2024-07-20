import json
import discord
from discord.ext import commands
from utils import utils 


buttonPath = "data/gameButtons.json"

class GameRoles(discord.ui.View):
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
        
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(content="ถอดยศหมาแล้วครับ", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(content="ให้ยศหมา ๆ แล้วครับ", ephemeral=True)

class gameRole(commands.Cog):
    def __init__(self, client):
        self.client = client
        
        self.ids = utils.load_ids()
        self.gameRoleChannelId = self.ids.get('gameRoleChannel_id')
    
    def save_ids(self):
        self.ids['gameRoleChannel_id'] = self.gameRoleChannelId
        utils.save_ids(self.ids)
    
    async def clear_channel(self, channel_id):
        channel = self.client.get_channel(channel_id)
        if isinstance(channel, discord.TextChannel):  # Ensure it's a text channel
            try:
                await channel.purge(limit=None)
            except Exception as e:
                print(f"Failed to clear channel {channel_id}: {e}")
        else:
            print(f"Channel with ID {channel_id} not found or not a text channel.")
    
    async def gameRoleEmbed(self, ctx = None, gameRoleChannelId = None):
        try:
                embed = discord.Embed(
                    title="**รับยศเกมที่เล่นครับ**",
                    description=f"กดตามปุ่มเกมที่เล่นเพื่อรับยศได้เลย กดอีกรอบเพื่อเอายศนั้น ๆ ออก",
                    color=0xB2BEB5
                )
                embed.set_image(url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTCQH_Iwy3xbLNb4f2FeNz01tTuhIUwuV5yFfCpINvItA&s")
                
                if gameRoleChannelId:
                    channel = self.client.get_channel(gameRoleChannelId)
                    if isinstance(channel, discord.TextChannel):  # Ensure the channel is a text channel
                        await channel.send(embed=embed, view=GameRoles())
                    else:
                        print(f"Channel with ID {gameRoleChannelId} not found or not a text channel.")
                #     return

                if ctx:
                    # Send the embed with buttons
                    message = await ctx.send(embed=embed, view=GameRoles())
                    # Delete the command message
                    await ctx.message.delete()
                
        except Exception as e:
            print(e)
    
    
    @commands.Cog.listener()
    async def on_ready(self):
        await self.clear_channel(self.gameRoleChannelId)
        await self.gameRoleEmbed(gameRoleChannelId=self.gameRoleChannelId)
    
    
    @commands.command(name="gameRole", description="รับยศ")
    async def gameRole(self, ctx):
        if ctx.author.guild_permissions.administrator:
            self.gameRoleChannelId = ctx.channel.id
            self.save_ids()
            await self.gameRoleEmbed(ctx)
        else:
            await ctx.send("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้", delete_after=10)

    @commands.command(name="addGameButton", description="เพิ่มปุ่มยศ", aliases = ["agb"])
    async def add_button(self, ctx, label: str, style: str, emoji: str, role_id: int):
        if ctx.author.guild_permissions.administrator:
            new_button = {
                "label": label,
                "style": style,
                "emoji": emoji[2:],
                "role_id": role_id
            }

            with open(buttonPath, "r") as f:
                buttons = json.load(f)

            buttons.append(new_button)

            with open(buttonPath, "w") as f:
                json.dump(buttons, f, indent=4)

            await ctx.send(f"ปุ่ม '{label}' ถูกเพิ่มเรียบร้อยแล้ว", delete_after=10)
        else:
            await ctx.send("คุณไม่มีสิทธิ์ในการใช้คำสั่งนี้", delete_after=10)

    @commands.command(name="removeButton", description="ลบปุ่มยศ")
    @commands.has_permissions(administrator=True)
    async def remove_button(self, ctx, label: str):
        try:
            with open(buttonPath, "r") as f:
                buttons = json.load(f)

            # Check the initial length of the buttons list
            initial_length = len(buttons)

            # Filter out the button with the given label
            buttons = [button for button in buttons if button["label"] != label]

            # Check the length after filtering
            final_length = len(buttons)

            if final_length < initial_length:
                with open(buttonPath, "w") as f:
                    json.dump(buttons, f, indent=4)
                
                await ctx.send(f"ปุ่ม '{label}' ถูกลบเรียบร้อยแล้ว", delete_after=10)
            else:
                await ctx.send(f"ไม่พบปุ่ม '{label}'", delete_after=10)

            # Delete the command message to keep the chat clean
            await ctx.message.delete()
        except Exception as e:
            print(e)
            await ctx.send(f"เกิดข้อผิดพลาด: {str(e)}", delete_after=10)
async def setup(client):
    await client.add_cog(gameRole(client))

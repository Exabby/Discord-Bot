from discord.ext import commands
import discord
import json

class Welcome(commands.Cog):
        def __init__(self, client):
            self.client = client
            
            
        welcomeChannel_id = None
        roleChannel_id = None
        
        @commands.command(name = "welcome")
        @commands.has_permissions(administrator=True)
        async def welcomeSetting(self, ctx, id1: str, id2: str):
                self.welcomeChannel_id = int(id1)
                self.roleChannel_id = int(id2)
                
                
                welcomeCh = self.client.get_channel(self.welcomeChannel_id)
                roleCh = self.client.get_channel(self.roleChannel_id)
                    
                    
                
                    
                await ctx.send(f">>> ข้อความ Welcome จะถูกส่งในห้องนี้ {welcomeCh.mention}\nและห้องรับโรลจะอยู่ตรงนี้ {roleCh.mention}")
           
        
            
        # Member Join in ***
        @commands.Cog.listener()
        async def on_member_join(self, member):
            channel = self.client.get_channel(self.welcomeChannel_id)
            roleChannel = self.client.get_channel(self.roleChannel_id)
            embed = discord.Embed(
                title="หวัดดีจ้า!",
                description=f"คนนี้มาทำไรอะ, {member.mention}!",
                color=0xB2BEB5
            )
        
            # Add guild icon if available
            if member.guild.icon.url:
                embed.set_thumbnail(url=member.guild.icon.url)

            # Set member avatar or default avatar
            if member.avatar:
                avatar_url = member.avatar.url
            else:
                avatar_url = member.default_avatar.url
        
            embed.set_thumbnail(url=avatar_url)
            embed.add_field(name="รับยศที่ห้องนี้", value=f"<#{roleChannel.id}> ยังไม่รับ ก็พูดไม่ได้นา", inline=True)
            embed.set_image(url="https://cdn.discordapp.com/icons/869618577106427974/a_acec8db6bb8253faf458f8cd544fe9a2.gif?size=128")
            embed.set_footer(text="อ่านไม")
        
            await channel.send(embed=embed)
            await member.send("ยินดีต้อนรับเข้าเซิฟครับพี่ ทำตัวติ๋ม ๆ ด้วย อย่าห้าว เดี๋ยวโดนเตะ!")
        @commands.Cog.listener()
        async def on_member_remove(self, member):
            channel = self.client.get_channel(1090300527411208314)
            try:
                await channel.send(f"คนนี้ไกปู {member.mention} ")
                print("Goodbye " + str(member))
            except Exception as e:
                print(f"An error occurred while sending the goodbye message: {e}")


async def setup(client):
    await client.add_cog(Welcome(client))




    
import asyncio
import discord
from discord.ext import commands
from tools.timeoutHandler import voteTimeoutApply

async def delete_message_after(commandMsg, message, duration):
        await asyncio.sleep(duration)
        await message.delete()
        await commandMsg.delete()

class VoteButton(discord.ui.Button):
    def __init__(self, vote_view, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.vote_view = vote_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.vote_view.members_in_vc:
            await interaction.response.send_message("ต้องอยู่ในห้อง ถึงจะโหวตได้", ephemeral=True)
            return

        if interaction.user in self.vote_view.voted_users:
            await interaction.response.send_message("โหวตไปแล้ว อย่ากดซ้ำครับน้อง", ephemeral=True)
            return

        self.vote_view.votes += 1
        self.vote_view.voted_users.add(interaction.user)
        await interaction.response.send_message(f"โหวตสำเร็จ คะแนนตอนนี้: {self.vote_view.votes}", ephemeral=True)

        if self.vote_view.votes >= self.vote_view.required_votes:
            self.vote_view.stop()

class VoteView(discord.ui.View):
    def __init__(self, ctx, member, duration, reason, vote_duration):
        super().__init__(timeout=vote_duration)
        self.ctx = ctx
        self.member = member
        self.duration = duration
        self.reason = reason
        self.vote_duration = vote_duration
        self.votes = 0
        self.voted_users = set()
        self.members_in_vc = ctx.author.voice.channel.members
        self.required_votes = (len(self.members_in_vc) // 2)
        
        self.add_item(VoteButton(self, label="👍"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user in self.members_in_vc

class VoteTimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voteDurationSecond = 60
    
    
            
    @commands.command(name="voteTimeout")
    async def voteTimeout(self, ctx, member: discord.Member, duration: int, *, reason: str):
        try:
            if not ctx.author.voice or not ctx.author.voice.channel:
                await ctx.send(f">>> โหวตใช้ได้เฉพาะคนที่อยู่ใน Voice Chat")
                return
            
            voice_channel = ctx.author.voice.channel
            members_in_vc = voice_channel.members
            
            vote_view = VoteView(ctx, member, duration, reason, self.voteDurationSecond)
            
            embed = discord.Embed(
                title="เริ่มโหวต",
                description=f"ให้ไอนี่ {member} \n สัก {duration} วิ ดีปะ?\n 0/**{vote_view.required_votes}**",
                color=0x2f3136
            )
            embed.add_field(name="ข้อหา", value=f"{reason}", inline=True)
            embed.set_footer(text=f"เวลาโหวตเหลือ {self.voteDurationSecond} วินาที")
            
            if member.avatar:
                avatar_url = member.avatar.url
            else:
                avatar_url = member.default_avatar.url
                
            embed.set_thumbnail(url=avatar_url)
            message = await ctx.send(embed=embed, view=vote_view)
            
            isDeleted = False
            
            # Start countdown
            for remaining in range(self.voteDurationSecond, 0, -1):
                embed.set_footer(text=f"เวลาโหวตเหลือ {remaining} วินาที")
                embed.description = f"ให้ไอนี่ {member} \n สัก {duration} วิ ดีปะ?\n {vote_view.votes}/**{vote_view.required_votes}**"
                await message.edit(embed=embed)
                if vote_view.votes >= vote_view.required_votes:
                    isDeleted = True
                    await message.delete()
                    deleteMsg = await ctx.send(f">>> โหวตครบ {member} โดน {duration} วินาที")
                    asyncio.create_task(delete_message_after(ctx.message, deleteMsg, duration))
                    await voteTimeoutApply(member, duration)
                    break
                await asyncio.sleep(1)
                
            if not isDeleted:
                await message.delete()
                await ctx.send(f">>> โหวตไม่พอนะครับ {member} ไม่โดน")
                
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")
            print(e)
            
    
async def setup(bot):
    await bot.add_cog(VoteTimeout(bot))

import asyncio
import discord

async def msgCheckTimeoutApply(message, timeout_duration):
    if message.author.voice is not None:
        await message.author.move_to(None)

    # Retrieve the timeout role
    timeout_role = discord.utils.get(message.guild.roles, name="Timeout")
    if timeout_role is None:
        await message.channel.send(">>> ไม่เจอยศ 'Timeout' สร้างก่อนนะพี่")
        return

    # Store the member's current roles
    current_roles = message.author.roles

    # Remove all roles from the member
    for role in current_roles:
        if role != message.guild.default_role:  # Don't remove the default role
            await message.author.remove_roles(role)

    # Add the timeout role to the member
    await message.author.add_roles(timeout_role)

    # Wait for the duration of the timeout, then remove the role
    await asyncio.sleep(timeout_duration)

    await message.author.remove_roles(timeout_role)

    # Add the original roles back to the member
    for role in current_roles:
        if role != message.guild.default_role:  # Don't add the default role
            await message.author.add_roles(role)

# async def voteTimeoutApply
async def voteTimeoutApply(member, duration):
    try:
        if member.voice is not None:
            await member.move_to(None)

        # Retrieve the timeout role
        timeout_role = discord.utils.get(member.guild.roles, name="Timeout")
        if timeout_role is None:
            await member.channel.send(">>> ไม่เจอยศ 'Timeout' สร้างก่อนนะพี่")
            return

        # Store the member's current roles
        current_roles = member.roles

        # Remove all roles from the member
        for role in current_roles:
            if role != member.guild.default_role:  # Don't remove the default role
                await member.remove_roles(role)

        # Add the timeout role to the member
        await member.add_roles(timeout_role)

        # Wait for the duration of the timeout, then remove the role
        await asyncio.sleep(duration)

        await member.remove_roles(timeout_role)

        # Add the original roles back to the member
        for role in current_roles:
            if role != member.guild.default_role:  # Don't add the default role
                await member.add_roles(role)
    except Exception as e:
        print(e)
import discord
from discord.ext import commands

import program
from utilities import logger


async def remove_role(member, role):
    await member.remove_roles(role)
    logger.log(f"The {role.name} has been revoked from {member}!")
    try:
        await member.send(f"The {role.name} role has been revoked!")
    except Exception:  # noqa
        logger.warn("Failed to message user - no access.")
        return


class ReactionRemoveListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        role = None
        root = program.config['reaction-roles']
        guild = discord.utils.find(lambda g: g.id == payload.guild_id, self.bot.guilds)

        if payload.message_id == root['message-id']:
            if str(payload.emoji) == '📰':
                role = guild.get_role(root['role-ids']['news'])
            elif str(payload.emoji) == '📢':
                role = guild.get_role(root['role-ids']['announcements'])
            elif str(payload.emoji) == '🤝':
                role = guild.get_role(root['role-ids']['job-offers'])

        if payload.message_id == root['verify']['message-id'] and str(payload.emoji) == '🔑':
            role = guild.get_role(root['verify']['default-role'])

        if role is not None:
            await remove_role(guild.get_member(payload.user_id), role)


async def setup(bot):
    await bot.add_cog(ReactionRemoveListener(bot))

import discord
from discord.ext import commands

import program
from utilities import logger


async def give_role(member, role):
    await member.add_roles(role)
    logger.log(f"{member} was given the {role.name} role!")
    try:
        await member.send(f"You have been assigned the {role.name} role!")
    except Exception:  # noqa
        logger.warn("Failed to message user - no access.")
        return


class ReactionAddListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member.bot:
            return

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
            await give_role(payload.member, role)


async def setup(bot):
    await bot.add_cog(ReactionAddListener(bot))

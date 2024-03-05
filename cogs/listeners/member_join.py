import discord
from discord.ext import commands

import program


class MemberJoin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title=f"Welcome to **{member.guild.name}**, {member.name}! :tada:", colour=program.colour)

        embed.add_field(name=program.config['welcome']['title'],
                        value=program.config['welcome']['description'],
                        inline=False)
        embed.set_thumbnail(url=member.avatar)

        await self.bot.get_channel(program.config['channel-ids']['welcome']).send(embed=embed)
        await member.add_roles(member.guild.get_role(program.config['settings']['default-role']))


async def setup(bot):
    await bot.add_cog(MemberJoin(bot))

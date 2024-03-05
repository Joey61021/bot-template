import os
import sys

sys.path.append(os.path.abspath('../../..'))

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

import program


class AdminCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.commands = [
            ('setup <verify/rules/roles/tickets>', 'Paste a bot function message in your channel!'),
            ('punishments', 'View all available punishment commands!'),
        ]

    @commands.group(name='admin')
    @has_permissions(administrator=True)
    async def admin(self, ctx):
        embed = discord.Embed(title=":police_officer: Admin Menu", colour=program.colour)

        for i, command in enumerate(self.commands, 1):
            embed.add_field(name=f"[{i}]. `{program.prefix}{command[0]}`",
                            value=command[1],
                            inline=False)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCmd(bot))

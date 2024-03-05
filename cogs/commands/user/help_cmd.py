import os
import sys
sys.path.append(os.path.abspath('../../..'))

import discord
from discord.ext import commands

import program
from program import cmd_cooldown


class HelpCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.commands = [
            ('music', 'Put on some beats!'),
            ('ping', 'Sends the bots ping!'),
            ('nerd <user>', 'Nerdify someone!'),
            ('random <num 1> <num 2>', 'Generates a random number within the range provided!'),
            ('rps <rock, paper, scissors>', 'Play rock paper scissors!'),
            ('avatar <user>', 'View user avatars!'),
            ('profile <user>', 'View user profiles!'),
            ('suggest <suggestion>', 'Send a suggestion!'),
            ('statistics', 'Displays interesting server statistics!'),
            ('admin', 'View the admin menu!'),
        ]

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(title=":blush: Help Menu", colour=program.colour)

        for i, command in enumerate(self.commands, 1):
            embed.add_field(name=f"[{i}]. `{program.prefix}{command[0]}`",
                            value=command[1],
                            inline=False)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCmd(bot))

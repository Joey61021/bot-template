import discord
from discord.ext import commands

import program
from program import cmd_cooldown


class StatisticsCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command()
    async def statistics(self, ctx):
        embed = discord.Embed(title=f"{ctx.guild.name} | Server Statistics", colour=program.colour)

        embed.add_field(name="Name:", value=f"{ctx.guild.name}", inline=True)
        embed.add_field(name="Owner:", value=f"{ctx.guild.owner}", inline=True)
        embed.add_field(name="All members:", value=len(ctx.guild.members), inline=True)
        embed.add_field(name="All humans:", value=len([m for m in ctx.guild.members if not m.bot]), inline=True)
        embed.add_field(name="All bots:", value=len([m for m in ctx.guild.members if m.bot]), inline=True)
        embed.add_field(name="All roles:", value=len(ctx.guild.roles), inline=True)
        embed.set_thumbnail(url=ctx.guild.icon)

        embed.set_footer(text=f"{ctx.author}", icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(StatisticsCmd(bot))

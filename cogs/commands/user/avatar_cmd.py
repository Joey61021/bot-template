import discord
from discord.ext import commands

import program
from program import cmd_cooldown


class AvatarCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="avatar", aliases=['pfp'])
    async def avatar(self, ctx, user: discord.User):
        embed = discord.Embed(title=f"{user.name}'s Avatar", colour=program.colour)
        embed.set_image(url=user.avatar.url)
        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)
        return


async def setup(bot):
    await bot.add_cog(AvatarCmd(bot))

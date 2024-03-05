import discord
from discord.ext import commands

import program
from program import cmd_cooldown


class ProfileCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="profile", usage="<user>")
    async def profile(self, ctx, user: discord.User = None):
        member = ctx.guild.get_member(ctx.author.id if user is None else user.id)

        embed = discord.Embed(title=f"{member.name} | Profile", colour=program.colour)

        embed.add_field(name="Bot:", value=f"{str(member.bot)}")
        embed.add_field(name="Current status:", value=f"{str(member.status).capitalize()}")
        embed.add_field(name="Joined server:", value=f"{ctx.guild.get_member(member.id).joined_at.strftime('%Y/%m/%d')}")
        embed.add_field(name="Account created:", value=f"{member.created_at.strftime('%Y/%m/%d')}")
        embed.add_field(name="Roles:", value="None" if len(member.roles) <= 1 else f"<@&{'>, <@&'.join([str(role.id) for role in member.roles[1:]])}>")
        embed.set_thumbnail(url=member.avatar.url)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(ProfileCmd(bot))

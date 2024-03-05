from discord.ext import commands

from program import cmd_cooldown


class PingCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! :ping_pong: **{round(self.bot.latency * 1000)}ms**")


async def setup(bot):
    await bot.add_cog(PingCmd(bot))

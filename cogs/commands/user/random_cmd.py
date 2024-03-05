import random

from discord.ext import commands

from program import cmd_cooldown


class RandomCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="random", usage="<num1> <num2>")
    async def random(self, ctx, num1: int, num2: int):
        await ctx.channel.send(f"The number is {random.randint(num1, num2)}! 🎲")


async def setup(bot):
    await bot.add_cog(RandomCmd(bot))

import random

import discord
from discord.ext import commands

from program import cmd_cooldown


async def check(ctx, pick, bot_pick):
    formatted = {"rock": "Rock :rock:", "paper": "Paper :paper:", "scissors": "Scissors :scissors:"}[bot_pick]

    if pick == bot_pick:  # Tie?
        await ctx.channel.send(embed=discord.Embed(title=f"We both picked {formatted}. It's a tie!",
                                                   color=discord.Colour.green()))
        return

    win = False
    if pick == "rock" and bot_pick == "scissors":
        win = True
    if pick == "paper" and bot_pick == "rock":
        win = True
    if pick == "scissors" and bot_pick == "paper":
        win = True

    await ctx.channel.send(embed=discord.Embed(title=f'I picked {formatted}, you ' + ("won!" if win else "lost!"),
                                               color=discord.Colour.green() if win else discord.Colour.red()))


class RockPaperScissorsCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="rps", usage="<rock, paper, scissors>")
    async def rps(self, ctx, choice: str):
        if not choice == "rock" and not choice == "paper" and not choice == "scissors":
            raise commands.BadArgument
        await check(ctx, choice, random.choice(["rock", "paper", "scissors"]))


async def setup(bot):
    await bot.add_cog(RockPaperScissorsCmd(bot))

import os
import sys

from managers import ticket_manager
from managers.messages import message_manager
from managers.messages.message_manager import Message

sys.path.append(os.path.abspath('../..'))

from discord.ext import commands

from program import cmd_cooldown


def in_guild(guild_id):
    async def predicate(ctx):
        return ctx.guild.id == guild_id

    return commands.check(predicate)


class CloseCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="close")
    async def invite(self, ctx):
        if not ctx.channel.name.startswith("ticket-"):
            await message_manager.error(ctx, Message.CMD_CLOSE_NOT_A_TICKET)
            return

        await ctx.channel.send("This ticket will be closed in 3 seconds...")
        await ticket_manager.close_ticket(ctx.channel)


async def setup(bot):
    await bot.add_cog(CloseCmd(bot))

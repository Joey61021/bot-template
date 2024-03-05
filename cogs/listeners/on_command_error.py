import discord
from discord.ext import commands

import program
from managers.messages import message_manager
from managers.messages.message_manager import Message
from utilities import logger


class OnCommandError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, discord.HTTPException, commands.CheckFailure)):
            return
        elif isinstance(error, commands.MissingPermissions):  # No permission
            await message_manager.error(ctx, Message.CMD_NO_PERMISSION)
            return
        elif isinstance(error, commands.CommandOnCooldown):  # Cooldown
            await message_manager.error(ctx,
                                        Message.CMD_COOLDOWN,
                                        time=round(error.retry_after))
            return
        elif isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
            usage = ctx.command.usage if ctx.command.usage is not None else ""
            await message_manager.error(ctx,
                                        Message.INVALID_USAGE,
                                        usage=f'{program.prefix}{ctx.command.name} {usage}')
            return
        elif isinstance(error, commands.UserNotFound):  # User not found
            await message_manager.error(ctx, Message.USER_NOT_FOUND)
            return
        logger.critical(error)


async def setup(bot):
    await bot.add_cog(OnCommandError(bot))

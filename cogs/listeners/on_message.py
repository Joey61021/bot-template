from discord.ext import commands

import program
from managers import suggestion_manager


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = program.config['suggestions']

    @commands.Cog.listener()
    async def on_message(self, message):
        user = message.author  # Staff suggestions
        if user.bot or not message.content.startswith(self.config['staff-prefix']):
            return

        if message.channel.id == self.config['channels']['staff']:
            await message.delete()
            await suggestion_manager.send_suggestion(user, message.channel, message.content[1:])


async def setup(bot):
    await bot.add_cog(OnMessage(bot))

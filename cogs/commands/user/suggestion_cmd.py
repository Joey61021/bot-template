import discord
from discord.ext import commands

import program
from managers import suggestion_manager
from managers.messages import message_manager
from managers.messages.message_manager import Message
from program import suggestion_cooldown
from utilities import logger


class SuggestionActionsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__()

        self.bot = bot
        self.timeout = None
        self.config = program.config['suggestions']

    async def disable_items(self, message):  # Disable buttons
        for item in self.children:
            item.disabled = True
        await message.edit(view=self)

    async def validate_submission(self, message: discord.Message):
        await self.disable_items(message)
        await message.edit(embed=discord.Embed(title="SUGGESTION HAS BEEN VALIDATED"))
        suggestion_manager.remove_pending(message.id)

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.success)
    async def action_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Submission has been **approved** by {interaction.user.global_name}!')
        user_id = suggestion_manager.get_data("user_id", interaction.message.id)
        suggestion = suggestion_manager.get_data("suggestion", interaction.message.id)

        await self.validate_submission(interaction.message)
        await suggestion_manager.send_suggestion(self.bot.get_user(user_id),
                                                 self.bot.get_channel(self.config['channels']['community']),
                                                 suggestion)
        try:  # Send dm
            channel = await message_manager.open_user_channel(self.bot, user_id)
            await channel.send(self.config['messages']['approved'])
        except:  # noqa
            pass

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.danger)
    async def action_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'Submission has been **denied** by {interaction.user.global_name}!')
        user_id = suggestion_manager.get_data("user_id", interaction.message.id)

        await self.validate_submission(interaction.message)
        try:  # Send dm
            channel = await message_manager.open_user_channel(self.bot, user_id)
            await channel.send(self.config['messages']['denied'])
        except:  # noqa
            pass


class SuggestionCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = program.config['suggestions']

    @commands.cooldown(1, suggestion_cooldown, commands.BucketType.user)
    @commands.command(name="suggestion", aliases=['suggest'], usage="<suggestion>")
    async def suggestion(self, ctx, *suggestion):
        suggestion = " ".join(suggestion)
        if len(suggestion) < 3 or len(suggestion) > 250:
            await message_manager.error(ctx, Message.CMD_SUGGESTION_MAX_CHAR)
            return
        if suggestion_manager.get_submission_count(ctx.author.id) >= self.config['submission-limit']:
            await message_manager.error(ctx,
                                        Message.CMD_SUGGESTION_LIMIT_REACHED,
                                        limit=self.config['submission-limit'])
            return
        await message_manager.send_embed(ctx, Message.CMD_SUGGESTION_SUBMITTED)
        try:
            channel = ctx.channel.guild.get_channel(self.config['channels']['validation'])
            message = await channel.send(embed=discord.Embed(title="AWAITING VALIDATION :clock1:",
                                                             description=f"Username: {ctx.author.global_name}"
                                                                         f"\nUser ID: {ctx.author.id}"
                                                                         f"\n\nSuggestion: {suggestion}",
                                                             colour=program.colour),
                                         view=SuggestionActionsView(self.bot))
        except AttributeError:
            logger.critical(f"Failed to send a message, does the channel still exist?")
            return
        suggestion_manager.set_pending(ctx.author.id, message.id, suggestion)


async def setup(bot):
    await bot.add_cog(SuggestionCmd(bot))

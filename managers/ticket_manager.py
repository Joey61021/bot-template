import asyncio
import os
from datetime import datetime

import discord

import program


class TicketOpenActions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Open a ticket", style=discord.ButtonStyle.blurple, custom_id="1")
    async def action_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        opened = get_opened_ticket(interaction.user.id, interaction.guild)
        if opened is not None:
            await interaction.response.send_message(f'You have an active ticket in <#{opened.id}>', ephemeral=True)
            return
        category = discord.utils.get(interaction.guild.categories, id=program.config['tickets']['category'])
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(send_messages=True, read_messages=True)
        }
        channel = await category.create_text_channel(name=f'ticket-{interaction.user.global_name}',
                                                     topic=f'{interaction.user.id} - Do not change',
                                                     overwrites=overwrites)

        await channel.send(embed=discord.Embed(title=f'{interaction.user.global_name} - Support Ticket',
                                               description="Please explain your issue and our team will be with you.",
                                               color=program.colour),
                           view=TicketActionsView())
        await interaction.response.send_message(f'A ticket has been opened for you in <#{channel.id}>', ephemeral=True)


class TicketActionsView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger)
    async def action_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=discord.Embed(title=f'Are you sure?',
                                               description="Closing this ticket will mark it as resolved.",
                                               color=program.colour),
                           view=CloseConfirmationView(), ephemeral=True)

    @discord.ui.button(label="Send Transcript", style=discord.ButtonStyle.blurple)
    async def action_two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await generate_transcript(interaction.channel)
        file_path = f'{interaction.channel.id}.md'
        with open(file_path, 'rb') as file:
            try:  # Attempt to DM user
                user_dm = await interaction.user.create_dm()
                await user_dm.send(file=discord.File(file_path))
                await interaction.response.send_message("The transcript has been sent to you!", ephemeral=True)
            except:  # noqa
                await interaction.response.send_message(file=discord.File(file_path), ephemeral=True)
            file.close()
        os.remove(file_path)


class CloseConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger)
    async def action_one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("This ticket will be closed in 3 seconds...")
        await close_ticket(interaction.channel)


async def close_ticket(channel):
    await asyncio.sleep(3)
    await generate_transcript(channel)

    file_path = f'{channel.id}.md'
    with open(file_path, 'rb') as file:
        for user in channel.members:
            if not user.bot:
                try:  # Attempt to DM user
                    user_dm = await user.create_dm()
                    await user_dm.send(file=discord.File(file_path))
                except:  # noqa
                    break
        file.close()

    os.remove(file_path)
    await channel.delete()


async def generate_transcript(channel):
    with open(f'{channel.id}.md', 'a') as file:
        file.write(f'Transcript generated on {datetime.now().strftime("%m/%d/%Y at %H:%M:%S")}\n\n')
        async for message in channel.history(limit=200, oldest_first=True):
            if not message.author.bot:
                file.write(f"{message.author} -> {message.clean_content}\n")
        file.close()


def get_opened_ticket(user_id, guild):
    category = discord.utils.get(guild.categories, id=program.config['tickets']['category'])
    for channel in category.text_channels:
        if str(channel.topic).split(' ')[0] == str(user_id):
            return channel
    return None

import os

import discord
import yaml
from discord.ext import commands
from discord.ext.commands import has_permissions

import program
from managers.messages import message_manager
from managers.messages.message_manager import Message
from managers.ticket_manager import TicketOpenActions
from program import cmd_cooldown

executable_dir = os.path.dirname(os.path.abspath(__file__))

faq = os.path.join(executable_dir, "./faq.yml")
guidelines = os.path.join(executable_dir, "./guidelines.yml")


class SetupCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="setup", usage="<verify/rules/roles>")
    @has_permissions(administrator=True)
    async def admin_setup(self, ctx, function: str):
        if function == "verify":
            await ctx.message.delete()
            embed = discord.Embed(title="Verification",
                                  description="Please read the outlined rules before entering the server.",
                                  colour=program.colour)

            message = await ctx.send(embed=embed)
            await message.add_reaction('🔑')
            return
        elif function == "rules":
            await ctx.message.delete()
            embed = discord.Embed(title="Server Guidelines",
                                  description="Failure to follow will lead to being banned.",
                                  colour=program.colour)

            with open(guidelines, 'r') as f:
                data = yaml.safe_load(f)
                for key, data in data.items():
                    embed.add_field(name=f"[{key}]. {data['title']}", value=data['content'])
                f.close()

            await ctx.send(embed=embed)
            return
        elif function == "roles":
            await ctx.message.delete()
            root = program.config['reaction-roles']['role-ids']

            embed = discord.Embed(title="Reaction roles are here!",
                                  description="React with the emoji to receive or remove the corresponding role!"
                                              f"\n\n📰 News - <@&{root['news']}>"
                                              f"\n📢 Announcements - <@&{root['announcements']}>"
                                              f"\n🤝 Job offers - <@&{root['job-offers']}>",
                                  colour=program.colour)

            message = await ctx.channel.send(embed=embed)
            await message.add_reaction('📰')
            await message.add_reaction('📢')
            await message.add_reaction('🤝')
        if function == "ticket" or function == "tickets":
            await ctx.message.delete()
            await ctx.send(embed=discord.Embed(title="Support tickets",
                                               description="Open a ticket to contact our team!",
                                               color=program.colour),
                           view=TicketOpenActions())
            return
        else:
            await message_manager.send_embed(ctx, Message.CMD_SETUP_TYPE_NOT_FOUND)


async def setup(bot):
    await bot.add_cog(SetupCmd(bot))

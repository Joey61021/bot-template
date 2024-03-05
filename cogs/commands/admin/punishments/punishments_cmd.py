import json
import os
import time
from enum import Enum

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions

import program
from managers.messages import message_manager
from managers.messages.message_manager import Message
from utilities import utils, logger

executable_dir = os.path.dirname(os.path.abspath(__file__))

temp_punishments = os.path.join(executable_dir, "temp_punishments.json")
punishment_log = os.path.join(executable_dir, "punishment_log.json")


class PunishmentType(Enum):
    WARN = {'title': "User warned", 'color': discord.Color.blurple()}
    KICK = {'title': "User kicked", 'color': discord.Color.orange()}
    BAN = {'title': "User banned", 'color': discord.Color.dark_red()}
    TEMP_BAN = {'title': "User temp banned", 'color': discord.Color.dark_red()}
    UNBAN = {'title': "User unbanned", 'color': discord.Color.green()}
    MUTE = {'title': "User muted", 'color': discord.Color.red()}
    TEMP_MUTE = {'title': "User temp muted", 'color': discord.Color.red()}
    UNMUTE = {'title': "User unmuted", 'color': discord.Color.green()}


async def has_temp_punishment(user_id):
    return str(user_id) in json.load(open(temp_punishments, 'r'))


def remove_temp_punishment(user_id):
    file = json.load(open(temp_punishments, "r"))
    del file[str(user_id)]
    json.dump(file, open(temp_punishments, "w"), indent=4)


class PunishmentsCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.ticker_task.start()
        self.mute_role_id = program.config['punishments']['mute-role']
        self.log_channel = program.config['punishments']['log-channel']

        self.subcommands = [
            ('kick <reason>', 'Kick user from server'),
            ('ban <user> <reason>', 'Ban user from the server'),
            ('temp_ban <user> <time> <reason>', 'Temporarily ban someone'),
            ('mute <user> <reason>', 'Mute someone'),
            ('temp_mute <user> <time> <reason>', 'Temporarily mute someone'),
            ('check <user>', 'Check a users punishment history'),
        ]

    async def warn_user(self, user, reason):
        try:
            channel = await message_manager.open_user_channel(self.bot, user)
            await channel.send(embed=discord.Embed(
                title="SERVER WARNING",
                description=f'You have received a warning for **{reason}**',
                colour=discord.Colour.orange()
            ))
        except:  # noqa
            pass

    async def temp_punish_user(self, ban: bool, guild, user, parsed_time):
        if await has_temp_punishment(user.id):
            remove_temp_punishment(user.id)

        try:
            await guild.ban(user) if ban else await utils.assign_role(user.id, self.mute_role_id, guild)
        except:  # noqa
            logger.critical("Unable to apply mute role or ban user, please check all values")

        file = json.load(open(temp_punishments, "r"))
        data = {
            "ban": ban,
            "guild_id": guild.id,
            "end_time": int(time.time()) + parsed_time
        }
        file[str(user.id)] = data
        json.dump(file, open(temp_punishments, "w"), indent=4)

    async def log_punishment(self, ctx, punishment_type, user, *reason):
        with open(punishment_log, "r") as log_file:
            log = json.load(log_file)

        user_id = str(user.id)

        if user_id not in log:
            log[user_id] = []  # Initialize

        data = {
            "type": str(punishment_type.name),
            "reason": " ".join(reason),
        }

        log[user_id].append(data)

        with open(punishment_log, "w") as log_file:
            json.dump(log, log_file, indent=4)

        channel = self.bot.get_channel(self.log_channel)
        await channel.send(embed=discord.Embed(title=f'{punishment_type.value["title"]}',
                                               description=f'User: **{user.name}**\n'
                                                           f'Reason: **{" ".join(reason)}**\n'
                                                           f'Punisher: **{ctx.author.name}**',
                                               colour=punishment_type.value["color"]))

    @tasks.loop(seconds=5)
    async def ticker_task(self):
        await self.bot.wait_until_ready()
        punishments = json.load(open(temp_punishments, "r"))

        if len(punishments) == 0:
            return

        for user_id, data in punishments.items():
            if int(time.time()) > data['end_time']:
                guild = self.bot.get_guild(data['guild_id'])
                if bool(data['ban']):
                    await guild.unban(user_id)
                else:
                    await utils.revoke_role(user_id, self.mute_role_id, guild)
                remove_temp_punishment(user_id)

    @commands.cooldown(1, program.cmd_cooldown, commands.BucketType.user)
    @commands.command(name="punishments", aliases=['punishment'])
    async def punishments(self, ctx):
        embed = discord.Embed(title=":rotating_light: Punishment Menu", colour=program.colour)

        for i, subcommand in enumerate(self.subcommands, 1):  # Collect subcommands
            embed.add_field(name=f"[{i}]. `{program.prefix}{subcommand[0]}`",
                            value=subcommand[1],
                            inline=False)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)
        return

    @commands.command(name="kick", usage="<user>")
    @has_permissions(manage_roles=True)
    async def kick(self, ctx, user: discord.User, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        await ctx.guild.kick(user)
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_KICK, user=user, reason=reason)
        await self.log_punishment(ctx, PunishmentType.KICK, user, reason)

    @commands.command(name="warn", usage="<user>")
    @has_permissions(manage_roles=True)
    async def warn(self, ctx, user: discord.User, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        await self.warn_user(user, reason)
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_WARN, user=user, reason=reason)
        await self.log_punishment(ctx, PunishmentType.WARN, user, reason)

    @commands.command(name="ban", usage="<user> <reason>")
    @has_permissions(administrator=True)
    async def ban(self, ctx, user: discord.User, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        await ctx.guild.ban(user)
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_BAN, user=user, reason=reason)
        await self.log_punishment(ctx, PunishmentType.BAN, user, reason)

    @commands.command(name="temp_ban", usage="<user> <time> <reason>")
    @has_permissions(administrator=True)
    async def temp_ban(self, ctx, user: discord.User, time_unit: str, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        parsed_time = utils.parse_time(time_unit)
        if parsed_time == -1 or parsed_time == -2:  # Is a valid time unit?
            await message_manager.error(ctx, Message.INVALID_TIME_UNIT)
            return

        await self.temp_punish_user(True, ctx.guild, user, parsed_time[0])
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_BAN, user=user, reason=reason, time=time_unit.lower())
        await self.log_punishment(ctx, PunishmentType.TEMP_BAN, user, reason)

    @commands.command(name="unban", usage="<user>")
    @has_permissions(administrator=True)
    async def unban(self, ctx, user: discord.User):
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        await ctx.guild.unban(user)
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_UNBAN, user=user.name)
        await self.log_punishment(ctx, PunishmentType.UNBAN, user, "n/a")

    @commands.command(name="mute", usage="<user> <reason>")
    @has_permissions(administrator=True)
    async def mute(self, ctx, user: discord.Member, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        try:
            role = discord.utils.get(ctx.guild.roles, id=int(self.mute_role_id))
            if role in user.roles:
                await message_manager.error(ctx, Message.CMD_PUNISHMENTS_ALREADY_MUTED)
                return
            await ctx.guild.get_member(int(user.id)).add_roles(role)
        except:  # noqa
            logger.critical("Failed to assign mute role, please check all values")

        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_MUTE, user=user, reason=reason)
        await self.log_punishment(ctx, PunishmentType.MUTE, user, reason)

    @commands.command(name="temp_mute", usage="<user> <time> <reason>")
    @has_permissions(administrator=True)
    async def temp_mute(self, ctx, user: discord.User, time_unit: str, *reason):
        reason = " ".join(reason) if len(reason) > 0 else "None"
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        parsed_time = utils.parse_time(time_unit)
        if parsed_time == -1 or parsed_time == -2:  # Is a valid time unit?
            await message_manager.error(ctx, Message.INVALID_TIME_UNIT)
            return

        await self.temp_punish_user(False, ctx.guild, user, parsed_time[0])
        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_TEMP_MUTE, user=user, reason=reason, time=time_unit.lower())
        await self.log_punishment(ctx, PunishmentType.TEMP_MUTE, user, reason)

    @commands.command(name="unmute", usage="<user>")
    @has_permissions(administrator=True)
    async def unmute(self, ctx, user: discord.Member):
        if not utils.check_permission_hierarchy(ctx.author, ctx.guild.get_member(user.id)):
            await message_manager.error(ctx, Message.CANNOT_PERFORM_TO_HIGHER)
            return

        try:
            role = discord.utils.get(ctx.guild.roles, id=int(self.mute_role_id))
            if role not in user.roles:
                await message_manager.error(ctx, Message.CMD_PUNISHMENTS_NOT_MUTED)
                return
            await ctx.guild.get_member(int(user.id)).remove_roles(role)
        except:  # noqa
            logger.critical("Failed to assign mute role, please check all values")

        await message_manager.send_embed(ctx, Message.CMD_PUNISHMENTS_UNMUTE, user=user)
        await self.log_punishment(ctx, PunishmentType.UNMUTE, user, "n/a")

    @commands.command(name="check", usage="<user>")
    @has_permissions(administrator=True)
    async def check(self, ctx, user: discord.User):
        log = json.load(open(punishment_log))
        data = log.get(str(user.id), [])
        count = len(data)

        if count < 1:  # User has no history
            await message_manager.error(ctx, Message.CMD_PUNISHMENTS_NO_HISTORY)
            return

        embed = discord.Embed(title=f"{user.name}'s history", description=f'Total items: **{count}**', colour=program.colour)
        for i, item in enumerate(reversed(data), 1):
            if i > 8:
                break
            embed.add_field(name=f'[{i}].', value=f'Type: **{item["type"]}**\nReason: **{item["reason"]}**', inline=False)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(PunishmentsCmd(bot))

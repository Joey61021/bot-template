import discord
from discord.ext.commands import MissingRequiredArgument

from utilities import logger


def check_permission_hierarchy(user: discord.Member, target: discord.Member):
    try:  # User/target value is missing?
        if user.top_role.position > target.top_role.position:
            return True
        else:
            return False
    except:  # noqa
        raise MissingRequiredArgument


async def assign_role(user_id, role_id, guild):
    try:
        role = discord.utils.get(guild.roles, id=int(role_id))
        await guild.get_member(int(user_id)).add_roles(role)
    except:  # noqa
        logger.critical("Failed to assign temp role, please check all values")


async def revoke_role(user_id, role_id, guild):
    try:
        role = discord.utils.get(guild.roles, id=int(role_id))
        await guild.get_member(int(user_id)).remove_roles(role)
    except:  # noqa
        logger.critical("Failed to revoke temp role, did the user leave?")


def parse_time(time):
    time_map = {"s": 1, "m": 60, "h": 3600, "d": 3600 * 24}
    i = {"s": "Seconds", "m": "Minutes", "h": "Hours", "d": "Days"}
    unit = time[-1]

    if unit not in ["s", "m", "h", "d"]:
        return -1
    try:
        val = int(time[:-1])

    except:  # noqa
        return -2

    if val == 1:
        return val * time_map[unit], i[unit][:-1]
    else:
        return val * time_map[unit], i[unit]

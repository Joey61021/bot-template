import json
import os
from enum import Enum

import discord

import program

executable_dir = os.path.dirname(os.path.abspath(__file__))
message_config = os.path.join(executable_dir, "messages.json")


class Message(Enum):
    # Generic
    CMD_COOLDOWN = ['generic', 'cooldown']
    CMD_NO_PERMISSION = ['generic', 'no-permission']
    INVALID_USAGE = ['generic', 'invalid-permission']
    USER_NOT_FOUND = ['generic', 'user-not-found']
    INVALID_TIME_UNIT = ['generic', 'invalid-time-unit']
    CANNOT_PERFORM_TO_HIGHER = ['generic', 'cannot-perform-to-higher']

    # Music
    CMD_MUSIC_ALREADY_CONNECTED = ['music', 'already-connected']
    CMD_MUSIC_COULD_NOT_CONNECT = ['music', 'could-not-connect']
    CMD_MUSIC_NOT_IN_VC = ['music', 'not-in-vc']
    CMD_MUSIC_CONNECTED = ['music', 'connected']
    CMD_MUSIC_DISCONNECTED = ['music', 'disconnected']
    CMD_MUSIC_RESUMED = ['music', 'resumed']
    CMD_MUSIC_REQUEST_TOO_SHORT = ['music', 'request-too-short']
    CMD_MUSIC_CANNOT_FIND_SONG = ['music', 'cannot-find-song']
    CMD_MUSIC_CANNOT_PLAY_LIVE = ['music', 'cannot-play-live']
    CMD_MUSIC_LOOP_ON = ['music', 'loop-on']
    CMD_MUSIC_LOOP_OFF = ['music', 'loop-off']
    CMD_MUSIC_PLAY_SONG = ['music', 'play-song']
    CMD_MUSIC_PAUSED = ['music', 'paused']
    CMD_MUSIC_ALREADY_PLAYING = ['music', 'already-playing']
    CMD_MUSIC_SKIPPED = ['music', 'skipped']
    CMD_MUSIC_NONE_TO_SKIP = ['music', 'none-to-skip']
    CMD_MUSIC_QUEUE_EMPTY = ['music', 'queue-empty']
    CMD_MUSIC_QUEUE_CLEARED = ['music', 'queue-cleared']
    CMD_MUSIC_QUEUE_SIZE_LIMITED = ['music', 'queue-size-limited']
    CMD_MUSIC_NONE_PLAYING = ['music', 'none-playing']

    # Suggestions
    APPROVED = ['suggestions', 'approved']
    DENIED = ['suggestions', 'denied']
    CMD_SUGGESTION_SUBMITTED = ['suggestions', 'submitted']
    CMD_SUGGESTION_MAX_CHAR = ['suggestions', 'max-char']
    CMD_SUGGESTION_LIMIT_REACHED = ['suggestions', 'limit-reached']

    # Close
    CMD_CLOSE_NOT_A_TICKET = ['close', 'not-a-ticket']

    # Punishments
    CMD_PUNISHMENTS_CANNOT_PUNISH_SELF = ['punishments', 'cannot-punish-self']
    CMD_PUNISHMENTS_UNABLE_TO_PUNISH = ['punishments', 'unable-to-punish']
    CMD_PUNISHMENTS_WARN = ['punishments', 'warn']
    CMD_PUNISHMENTS_KICK = ['punishments', 'kick']
    CMD_PUNISHMENTS_BAN = ['punishments', 'ban']
    CMD_PUNISHMENTS_TEMP_BAN = ['punishments', 'temp-ban']
    CMD_PUNISHMENTS_UNBAN = ['punishments', 'unban']
    CMD_PUNISHMENTS_MUTE = ['punishments', 'mute']
    CMD_PUNISHMENTS_ALREADY_MUTED = ['punishments', 'already-muted']
    CMD_PUNISHMENTS_TEMP_MUTE = ['punishments', 'temp-mute']
    CMD_PUNISHMENTS_UNMUTE = ['punishments', 'unmute']
    CMD_PUNISHMENTS_NOT_MUTED = ['punishments', 'not-muted']
    CMD_PUNISHMENTS_NO_HISTORY = ['punishments', 'no-history']

    # Setup
    CMD_SETUP_TYPE_NOT_FOUND = ['setup', 'type-not-found']


def get_message(msg: Message):
    with open(message_config, 'r', encoding='utf-8') as file:
        messages = json.load(file)

    for key in msg.value:
        if key in messages:
            messages = messages[key]
    return messages if messages else "There was an error finding this message, please contact an admin!"


async def send_message(ctx, msg: Message, **kwargs):
    await ctx.channel.send(get_message(msg).format(**kwargs))


async def send_embed(ctx, msg: Message, **kwargs):
    await ctx.channel.send(embed=discord.Embed(title=get_message(msg).format(**kwargs), colour=program.colour))


async def error(ctx, msg: Message, **kwargs):
    await ctx.send(embed=discord.Embed(title=f':x: {get_message(msg).format(**kwargs)}', colour=discord.Color.red()))


async def open_user_channel(bot, user_id):
    try:
        return await bot.create_dm(bot.get_user(int(user_id)))
    except:  # noqa
        return

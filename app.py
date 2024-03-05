import os
import platform

import discord
import discord.utils
import pyfiglet
from discord.ext import commands

import program
from managers import database_manager
from managers.ticket_manager import TicketOpenActions
from utilities import logger


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=program.prefix, help_command=None, intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        self.add_view(TicketOpenActions())


bot = PersistentViewBot()


async def load_cogs():
    logger.log("Loading available cogs...")
    total, loaded = 0, 0  # Total cogs found/total loaded cogs

    for root, dirs, files in os.walk('cogs'):
        for file in files:
            if file.endswith(".py"):

                total += 1
                try:
                    file_path = os.path.join(root, file[:-3]).replace('\\', ".").replace('/', ".")
                    await bot.load_extension(file_path)
                    loaded += 1
                except Exception as err:
                    logger.critical(err)

    logger.success(f'Successfully loaded {loaded}/{total} cogs')  # Success message


@bot.event
async def on_ready():
    await load_cogs()  # Load cogs
    await database_manager.connect()  # Load database

    # Assign bot status
    status = program.config['settings']['status'].replace("{prefix}", program.prefix)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=status))
    logger.connection(f'{bot.user} connected to {len(bot.guilds)} guilds with status "{status}"!')

    # Startup info messages
    logger.info("\nBot info:\n"
                f"   Prefix: {program.prefix}\n"
                f"   Username: {bot.user.name}\n"
                f"   Author: {program.author}\n")
    logger.info(f"Version info:\n"
                f"   Bot Version: {program.version}\n"
                f"   Python version: {platform.version()}\n"
                f"   Discord version: {discord.__version__}\n")


def start():
    print(pyfiglet.figlet_format("Aurora"))

    # Token
    with open('resources/TOKEN.txt') as f:
        token = f.read().strip()
        if len(token) <= 1:
            logger.critical("Bot token not found in TOKEN.txt!")
            return
        bot.run(token)


start()

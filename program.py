import discord
import yaml

config = yaml.safe_load(open('resources/config.yml', 'r'))

# Bot
name = "AuroraBot"
version = "1.0.0"
author = "Texxyy"

# Settings
colour = discord.Colour.dark_blue()
prefix = config['settings']['prefix']

# Cool-downs
cmd_cooldown = config['settings']['cmd_cooldown']
suggestion_cooldown = config['suggestions']['cooldown']

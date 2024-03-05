import os
from io import BytesIO

import discord
import requests
from PIL import Image
from discord.ext import commands

import program
from program import cmd_cooldown

executable_dir = os.path.dirname(os.path.abspath(__file__))
glasses_image = os.path.join(executable_dir, "../../../media/glasses.png")


class NerdCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="nerd", usage="<user>")
    async def nerd(self, ctx, user: discord.User):
        avatar = Image.open(BytesIO(requests.get(user.avatar.url).content))
        nerd_glasses = Image.open(glasses_image).resize(avatar.size)

        # Paste the nerd glasses on the avatar
        avatar.paste(nerd_glasses, (0, 0), nerd_glasses)
        modified_image = BytesIO()
        avatar.save(modified_image, 'PNG')
        modified_image.seek(0)

        embed = discord.Embed(title=f'{user.name} has been nerdified! :nerd:', colour=program.colour)
        embed.set_image(url="attachment://nerd_avatar.png")
        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed, file=discord.File(modified_image, "nerd_avatar.png"))
        return


async def setup(bot):
    await bot.add_cog(NerdCmd(bot))

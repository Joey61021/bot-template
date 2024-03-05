import re
from datetime import timedelta, datetime

import discord
from discord.ext import commands
from yt_dlp import YoutubeDL

import program
from managers.messages import message_manager
from managers.messages.message_manager import Message
from program import cmd_cooldown
from utilities import logger


def user_in_vc(ctx):
    return ctx.author.voice is not None


class MusicCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subcommands = [
            ('join/j', 'Join your channel!'),
            ('leave/l/quit', 'Leave your channel!'),
            ('play/p <title/url>', 'Listen to some music!'),
            ('repeat', 'Play it on repeat'),
            ('pause', 'Pause the song'),
            ('resume', 'Resume listening'),
            ('skip/s', 'Skip to the next song!'),
            ('queue/q', 'See whats next'),
            ('clear', 'Clear the queue'),
            ('playing/curr', 'What am I listening to?')
        ]

        self.is_playing = False
        self.is_paused = False
        self.is_looped = False

        self.curr_playing = None
        self.song_started = None
        self.idle_stamp = None

        self.music_queue = []
        self.queue_limit = program.config['settings']['music-queue-limit']

        self.YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 200M',
            'options': '-vn'
        }

        self.vc = None

    async def search(self, ctx, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                if re.match(r'^https?://', item):  # Item is a URL?
                    info = ydl.extract_info(item, download=False)
                else:
                    info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries']

                video = info if info else None
                if video:
                    if isinstance(video, list):
                        video = video[0]
                    return {
                        'id': video['id'],
                        'url': video['url'],
                        'title': video['title'],
                        'uploader': video['uploader'],
                        'duration': video['duration'],
                        'requester': ctx.author.name
                    }
                else:
                    await message_manager.send_embed(ctx, Message.CMD_MUSIC_CANNOT_FIND_SONG)
                    return False
            except Exception as err:  # noqa
                logger.critical(err)
                await message_manager.send_embed(ctx, Message.CMD_MUSIC_CANNOT_PLAY_LIVE)
                return False

    def play_next(self):
        try:
            if len(self.music_queue) > 0 or self.is_looped:
                self.is_playing = True

                if not self.is_looped:
                    self.curr_playing = self.music_queue[0]
                    self.music_queue.pop(0)

                self.vc.play(discord.FFmpegPCMAudio(self.curr_playing[0]['url'], **self.FFMPEG_OPTIONS),
                             after=lambda e: self.play_next())
                self.song_started = datetime.now()
                self.idle_stamp = None
            else:
                self.curr_playing = None
                self.is_playing = False
        except:  # noqa
            return

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            song = self.music_queue[0][0]

            if self.vc is None or not self.vc.is_connected:
                self.vc = await self.music_queue[0][1].connect()

                if self.vc is None:
                    await message_manager.send_embed(ctx, Message.CMD_MUSIC_COULD_NOT_CONNECT)
                    return
                else:
                    await self.vc.move_to(self.music_queue[0][1])

            self.vc.play(discord.FFmpegPCMAudio(song['url'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
            self.song_started = datetime.now()
            self.curr_playing = self.music_queue[0]

            embed = discord.Embed(title=":musical_note: Now playing", colour=program.colour)
            embed.add_field(name=f"Title:", value=song['title'], inline=False)
            embed.add_field(name=f"Duration:", value=timedelta(seconds=song['duration']), inline=True)
            embed.add_field(name=f"Uploader:", value=song['uploader'], inline=True)
            embed.add_field(name=f"Requested by:", value=song['requester'], inline=True)
            embed.set_thumbnail(url=f"https://img.youtube.com/vi/{song['id']}/0.jpg")

            view = discord.ui.View()  # Button
            view.add_item(discord.ui.Button(label="Watch on YouTube",
                                            style=discord.ButtonStyle.url,
                                            url=f"https://youtu.be/{song['id']}"))

            self.music_queue.pop(0)
            await ctx.send(embed=embed, view=view)

    async def disconnect(self):
        self.music_queue = []
        self.is_looped = None
        self.curr_playing = None
        self.is_playing = False
        self.is_paused = False
        self.song_started = None
        self.idle_stamp = None

        await self.vc.stop()
        await self.vc.disconnect()

        self.vc = None

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="music")
    async def music(self, ctx):
        embed = discord.Embed(title=":notes: Music Menu", colour=program.colour)

        for i, subcommand in enumerate(self.subcommands, 1):  # Collect subcommands
            embed.add_field(name=f"[{i}]. `{program.prefix}{subcommand[0]}`", value=subcommand[1], inline=True)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)
        return

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="join", aliases=['j'])
    async def join(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        vc = ctx.author.voice.channel
        await message_manager.send_embed(ctx, Message.CMD_MUSIC_CONNECTED)
        if ctx.voice_client is None:
            self.vc = await vc.connect()
        else:
            self.vc = await ctx.voice_client.move_to(vc)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="leave", aliases=['l', 'quit'])
    async def leave(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        await self.disconnect()
        await message_manager.send_embed(ctx, Message.CMD_MUSIC_DISCONNECTED)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="play", aliases=['p'], usage="<title/url>")
    async def play(self, ctx, *, search=None):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return
        elif self.is_paused:  # Resume if paused
            self.is_playing = True
            self.is_paused = False
            self.song_started = self.song_started if not self.idle_stamp else (self.song_started - (self.idle_stamp - datetime.now()))
            self.idle_stamp = None
            self.vc.resume()
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_RESUMED, song=self.curr_playing[0]['title'])
        else:
            if len(self.music_queue) >= self.queue_limit:  # Queue reached size limit
                await message_manager.error(ctx, Message.CMD_MUSIC_QUEUE_SIZE_LIMITED, size=self.queue_limit)
                return
            query = "".join(search)
            if len(query) < 3:  # Less than 3 characters
                await message_manager.error(ctx, Message.CMD_MUSIC_REQUEST_TOO_SHORT)
                return

            await ctx.send(f"Searching for **{query}**...")
            song = await self.search(ctx, query)
            if not isinstance(song, bool):
                self.music_queue.append([song, ctx.author.voice.channel])

                if not self.is_playing:
                    await self.play_music(ctx)
                    return

                # Message
                embed = discord.Embed(title=":alarm_clock: Added to queue", colour=program.colour)

                embed.add_field(name=f"Title:", value=song['title'], inline=False)
                embed.add_field(name=f"Duration:", value=timedelta(seconds=song['duration']), inline=True)
                embed.add_field(name=f"Uploader:", value=song['uploader'], inline=True)
                embed.add_field(name=f"Requested by:", value=ctx.author.name, inline=True)
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{song['id']}/0.jpg")

                view = discord.ui.View()  # Button
                view.add_item(discord.ui.Button(label="Watch on YouTube",
                                                style=discord.ButtonStyle.url,
                                                url=f"https://youtu.be/{song['id']}"))

                await ctx.send(embed=embed, view=view)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="repeat", aliases=['r', 'loop'])
    async def repeat(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        if self.is_playing and not self.is_paused:
            if self.is_looped:
                self.is_looped = False
                await message_manager.send_embed(ctx, Message.CMD_MUSIC_LOOP_OFF)
                return
            self.is_looped = True
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_LOOP_ON)
        else:
            await message_manager.error(ctx, Message.CMD_MUSIC_PLAY_SONG)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="pause", aliases=['stop'])
    async def pause(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
            self.idle_stamp = datetime.now()
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_PAUSED)
        elif self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.song_started = self.song_started if not self.idle_stamp else (self.song_started - (self.idle_stamp - datetime.now()))
            self.idle_stamp = None
            self.vc.resume()
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_RESUMED, song=self.curr_playing[0]['title'])

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="resume")
    async def resume(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.song_started = self.song_started if not self.idle_stamp else (self.song_started - (self.idle_stamp - datetime.now()))
            self.idle_stamp = None
            self.vc.resume()
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_RESUMED, song=self.curr_playing[0]['title'])
            return
        await message_manager.error(ctx, Message.CMD_MUSIC_ALREADY_PLAYING)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="skip", aliases=['s'])
    async def skip(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        if self.vc is not None and self.vc:
            self.vc.stop()
            await message_manager.send_embed(ctx, Message.CMD_MUSIC_SKIPPED)
            await self.play_music(ctx)
            return
        await message_manager.error(ctx, Message.CMD_MUSIC_NONE_TO_SKIP)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="queue", aliases=['q'])
    async def queue(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        retval = []
        for i in range(0, len(self.music_queue)):  # Append entries
            retval.append(self.music_queue[i][0]['title'])

        if len(retval) > 0:  # Queue is not empty
            embed = discord.Embed(title="🎶 Music Queue", colour=program.colour)

            for i in range(0, len(retval)):  # Loop queued songs
                embed.add_field(name=f"[{i}].", value=retval[i], inline=True)

            embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
            await ctx.send(embed=embed)
        else:
            await message_manager.error(ctx, Message.CMD_MUSIC_QUEUE_EMPTY)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="clear")
    async def clear(self, ctx):
        if not user_in_vc(ctx):  # User is not in a vc
            await message_manager.error(ctx, Message.CMD_MUSIC_NOT_IN_VC)
            return

        self.music_queue = []
        self.is_playing = False
        self.is_paused = False

        await message_manager.send_embed(ctx, Message.CMD_MUSIC_QUEUE_CLEARED)

    @commands.cooldown(1, cmd_cooldown, commands.BucketType.user)
    @commands.command(name="playing", aliases=['curr'])
    async def playing(self, ctx):
        if self.curr_playing is None:  # Song currently playing?
            await message_manager.error(ctx, Message.CMD_MUSIC_NONE_PLAYING)
            return

        def calc_duration():
            idle_time = 0 if not self.idle_stamp else (self.idle_stamp - datetime.now()).total_seconds()
            percentage = (((datetime.now() - self.song_started).total_seconds() - idle_time)/self.curr_playing[0]['duration'])*100
            black_squares = int(10 * (1 - percentage / 100))
            white_squares = 10 - black_squares

            return ("⬜" * white_squares + "⬛" * black_squares).strip()

        def calc_time_left():
            idle_time = 0 if not self.idle_stamp else (self.idle_stamp - datetime.now()).total_seconds()
            return round((self.curr_playing[0]['duration']-(datetime.now() - self.song_started).total_seconds()) - idle_time)

        def get_next_playing():
            try:  # Get the next song in the queue
                retval = self.music_queue[0][0]['title']
            except:  # noqa
                retval = "Nothing yet!"
            return retval

        embed = discord.Embed(title=f":headphones: {self.curr_playing[0]['title']}", colour=program.colour)

        embed.add_field(name=f"{timedelta(seconds=calc_time_left())} remaining", value=calc_duration(), inline=True)
        embed.add_field(name=f"Uploader:", value=self.curr_playing[0]['uploader'], inline=True)
        embed.add_field(name=f"Paused:", value=str(self.is_paused), inline=True)
        embed.add_field(name=f"Looped:", value=str(self.is_looped), inline=True)
        embed.add_field(name=f"Queue size:", value=len(self.music_queue), inline=True)
        embed.add_field(name=f"Up next:", value=get_next_playing(), inline=True)

        embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel and self.vc is not None:
            if self.vc.channel is before.channel and len(before.channel.members) == 1:
                await self.disconnect()


async def setup(bot):
    await bot.add_cog(MusicCmd(bot))

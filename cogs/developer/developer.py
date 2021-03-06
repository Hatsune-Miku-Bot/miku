import os
import subprocess as sp
import time
from pathlib import Path

import discord
from discord import embeds
from discord.ext import commands


async def create_paginator(bot, ctx, pages):
    msg = await ctx.send(embed=pages[0])

    for reaction in ["⏮️", "◀️", "⏹️", "▶️", "⏭️"]:
        await msg.add_reaction(reaction)

    await bot.state.sadd(
        "reaction_menus",
        {
            "kind": "paginator",
            "channel": msg.channel.id,
            "message": msg.id,
            "end": int(time.time()) + 180,
            "data": {
                "page": 0,
                "all_pages": [page.to_dict() for page in pages],
            },
        },)


class Embed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.random()

        super().__init__(**kwargs)


class ErrorEmbed(embeds.Embed):
    def __init__(self, **kwargs):
        if "colour" not in kwargs:
            kwargs["colour"] = discord.Color.red()

        super().__init__(**kwargs)


class Developer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.appleapiisbad = True
        self.description = 'These set of commands are only locked to the developer'

    def owners(ctx):
        return ctx.author.id == 571889108046184449

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.check(owners)
    async def dev(self, ctx, command=None):
        '''These set of commands are only locked to the developer'''
        command2 = self.bot.get_command(f"{command}")
        if command2 is None:
            await ctx.send_help(ctx.command)
        else:
            if command is None:
                await ctx.send_help(ctx.command)
            else:

                pass

    @dev.group(name='sharedservers', usage="<user>")
    async def sharedservers(self, ctx, *, user: discord.Member):
        '''Get a list of servers the bot shares with the user.'''
        guilds = [
            f"{guild.name} `{guild.id}` ({guild.member_count} members)"
            for guild in [
                guild for guild in user.mutual_guilds
            ]
        ]

        await self._send_guilds(ctx, guilds, "Shared Servers")

    @dev.group(usage="<server ID>")
    async def createinvite(self, ctx, *, argument: int):
        '''Create an invite to the specified server'''
        try:
            guild = self.bot.get_guild(int(argument))
        except:
            await ctx.send(embed=ErrorEmbed(description="Guild not found"))
            return
        try:
            invite = (await guild.invites())[0]
        except (IndexError, discord.Forbidden):
            try:
                invite = (await guild.text_channels())[0].create_invite(max_age=120)
            except (IndexError, discord.Forbidden):
                await ctx.send(embed=ErrorEmbed(description="No permissions to create an invite link."))
                return

        await ctx.send(embed=Embed(description=f"Here is the invite link: {invite.url}"))

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def load(self, ctx, name: str):
        """Loads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"Loaded extension **`cogs/{name}.py`**")

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def reload(self, ctx, name: str):
        """Reloads an extension. """
        try:
            self.bot.reload_extension(f"cogs.{name}")
            await ctx.message.add_reaction('🔄')

        except Exception as e:
            return await ctx.send(f"```py\n{e}```")

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def unload(self, ctx, name: str):
        """Unloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"```py\n{e}```")
        await ctx.send(f"📤 Unloaded extension **`cogs/{name}.py`**")

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def reloadall(self, ctx):
        """Reloads all extensions. """

        cog_dir = Path(__file__).resolve(strict=True).parent.parent
        error_collection = []
        for file in os.listdir(cog_dir):
            if os.path.isdir(cog_dir / file):
                for i in os.listdir(cog_dir / file):
                    if i.endswith('.py'):
                        try:
                            self.bot.reload_extension(
                                f"cogs.{file.strip(' ')}.{i[:-3]}")
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")
            else:
                if file.endswith('.py'):
                    if file != 'music1.py':
                        try:
                            self.bot.reload_extension(f'bot.cogs.{file[:-3]}')
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")

        if error_collection:
            output = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{output}"
            )

        await ctx.send("**`Reloaded All Extentions`**")

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def sync(self, ctx):
        """Sync with GitHub and reload all the cogs"""
        embed = discord.Embed(
            title="Syncing...", description=":joy: Syncing and reloading cogs.")
        embed.set_footer(text=f"{ctx.author} | Minato Namikaze")
        msg = await ctx.send(embed=embed)
        async with ctx.channel.typing():
            output = sp.getoutput('git pull')
        embed = discord.Embed(
            title="Synced", description="Synced with GitHub and reloaded all the cogs.")
        # Reload Cogs as well
        cog_dir = Path(__file__).resolve(strict=True).parent.parent
        error_collection = []
        for file in os.listdir(cog_dir):
            if os.path.isdir(cog_dir / file):
                for i in os.listdir(cog_dir / file):
                    if i.endswith('.py'):
                        try:
                            self.bot.reload_extension(
                                f"cogs.{file.strip(' ')}.{i[:-3]}")
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")
            else:
                if file.endswith('.py'):
                    if file != 'music1.py':
                        try:
                            self.bot.reload_extension(f'bot.cogs.{file[:-3]}')
                        except Exception as e:
                            return await ctx.send(f"```py\n{e}```")

        if error_collection:
            err = "\n".join(
                [f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"Attempted to reload all extensions, was able to reload, "
                f"however the following failed...\n\n{err}"
            )

        await msg.edit(embed=embed)

    @dev.group(invoke_without_command=True)
    @commands.check(owners)
    async def changestat(self, ctx):
        '''Change the bot status'''
        await ctx.send(f"Hi yeah")

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def stream(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        '''Streaming Activity'''
        await self.bot.change_presence(activity=discord.Streaming(status=discord.Status.idle, name=activity, url="http://www.twitch.tv/transhelperdiscordbot"))
        await ctx.send(f'Changed activity to **{activity}** using **Stream status**.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def game(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        '''Game Activity'''
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=activity))
        await ctx.send(f'Changed activity to **{activity}** using **Game status**.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def watching(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        '''Watching activity'''
        await self.bot.change_presence(activity=discord.Activity(status=discord.Status.idle, type=discord.ActivityType.watching, name=activity))
        await ctx.send(f'Changed activity to **{activity}** using **Watching status**.')

    @changestat.group(invoke_without_command=True)
    @commands.check(owners)
    async def listening(self, ctx, *, activity='placeholder (owner to lazy lol)'):
        '''Listenting Activity'''
        await self.bot.change_presence(activity=discord.Activity(status=discord.Status.idle, type=discord.ActivityType.listening, name=activity))
        await ctx.send(f'Changed activity to **{activity}** using **Listening status**.')


def setup(bot):
    bot.add_cog(Developer(bot))

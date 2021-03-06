import discord
from discord.ext import commands
import json
from utils import language, tasks
from utils import commands as command


class Ban(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def safe_ban(member: discord.Member, reason: str):
        try:
            await member.ban(reason=reason)
        except:
            raise commands.errors.BotMissingPermissions("ban_members")

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        if command.if_command_disabled(ctx.command.name, ctx.guild):
            return
        # Getting all translations
        lang = language.get_server_lang(ctx.guild)
        useful = lang["translations"]["ban"]

        # If user has perms to ban
        if ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator:

            # Ban the member
            await self.safe_ban(member, reason)

            # Creates and sends the response embed
            response_embed = discord.Embed(title=useful["banned"].replace("%%member%%", member.display_name).replace("%%reason%%", reason), color=0xdb2a2a)
            await ctx.send(embed=response_embed)

    @commands.command()
    async def tempban(self, ctx: commands.Context, user: discord.User, *, args):
        if command.if_command_disabled(ctx.command.name, ctx.guild):
            return
        # Getting all translations
        lang = language.get_server_lang(ctx.guild)
        useful = lang["translations"]["ban"]

        # If user has perms to ban
        if ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator:
            args, endtime = await tasks.process_time(ctx, args, useful["invalid_time"])

            # Figuring ot if something went
            if args == "err":
                return

            # If reason is empty
            elif args == "":
                reason = "No reason provided"

            # Else the reason is the remains of args
            else:
                reason = args

            # If the reason length exceeds the maximum length for a reason
            if len(reason) > 256:
                response_embed = discord.Embed(title=useful["too_long"], color=0xdb2a2a)
                await ctx.send(embed=response_embed); return

            # Schedule the unban
            with open("config/tasks.json", "r") as f:
                reminders = json.load(f)

            with open("config/tasks.json", "w") as f:
                reminders[str(round(endtime))] = {"unban": {"user": user.id, "guild": ctx.guild.id}}
                json.dump(reminders, f, indent=4)

            # Safely ban he member
            member: discord.Member = ctx.guild.get_member(user.id)
            await self.safe_ban(member, reason)

            response_embed = discord.Embed(title=useful["tempbanned"].replace("%%member%%", member.display_name).replace("%%reason%%", reason), color=0xdb2a2a)

            await ctx.send(embed=response_embed)


def setup(client):
    client.add_cog(Ban(client))


if __name__ == "__main__":
    import sys
    import os
    import pathlib

    os.system(f"{sys.executable} {pathlib.Path(__file__).parent.absolute()}/../main.py")

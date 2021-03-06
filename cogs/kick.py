import discord
from discord.ext import commands
from utils import language
from utils import commands as command


class Kick(commands.Cog):

    def __init__(self, client):
        self.client = client

    @staticmethod
    async def safe_kick(member, reason):
        try:
            await member.kick(reason=reason)
        except:
            raise commands.errors.BotMissingPermissions("kick_members")

    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        if command.if_command_disabled(ctx.command.name, ctx.guild):
            return
        # Getting all translations
        lang = language.get_server_lang(ctx.guild)
        useful = lang["translations"]["kick"]

        # If user has perms to kick
        if ctx.author.guild_permissions.kick_members or ctx.author.guild_permissions.administrator:
            # Kick the member
            await self.safe_kick(member, reason)

            # Creates and sends the response embed
            response_embed = discord.Embed(title=useful["kicked"].format("%%member%%", member).replace("%%reason%%", reason), color=0xdb2a2a)
            await ctx.send(embed=response_embed)


def setup(client):
    client.add_cog(Kick(client))


if __name__ == "__main__":
    import sys
    import os
    import pathlib
    os.chdir(f"{pathlib.Path(__file__).parent.absolute()}/..")
    os.system(f"{sys.executable} {pathlib.Path(__file__).parent.absolute()}/../main.py")

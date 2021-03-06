import discord
from discord.ext import commands
from urllib.parse import quote as valid_url
from utils import language
from utils import commands as command


class Wiki(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["wikipedia"])
    async def wiki(self, ctx, *, search):
        if command.if_command_disabled(ctx.command.name, ctx.guild):
            return
        search = valid_url(search)
        url = discord.Embed(title=f"https://{language.get_server_lang_code(ctx.guild).split('_')[0]}.wikipedia.org/wiki/{search}")
        await ctx.send(embed=url)


def setup(client):
    client.add_cog(Wiki(client))


if __name__ == "__main__":
    import sys
    import os
    import pathlib

    os.system(f"{sys.executable} {pathlib.Path(__file__).parent.absolute()}/../main.py")

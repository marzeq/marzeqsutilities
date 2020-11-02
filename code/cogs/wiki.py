import discord
from discord.ext import commands
from urllib.parse import quote as valid_url


class Wiki(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["wikipedia"])
    async def wiki(self, ctx, *, search):
        search = valid_url(search)
        url = discord.Embed(title=f"https://{self.client.get_server_lang_code(ctx.guild.id).split('_')[0]}.wikipedia.org/wiki/{search}")
        await ctx.send(embed=url)


def setup(client):
    client.add_cog(Wiki(client))
import discord
from discord.ext import commands


class Ban(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided."):
        if ctx.author.guild_permissions.ban_members or ctx.author.guild_permissions.administrator:
            await member.ban(reason=reason)


def setup(client):
    client.add_cog(Ban(client))
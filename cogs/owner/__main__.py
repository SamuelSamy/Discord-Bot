import discord

from discord.ext import commands


class Owner(commands.Cog):

    def __init__ (self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def leave(self, ctx, guild : discord.Guild):
        await guild.leave()
        await ctx.reply(f"Succsefully left `{guild.name}`")


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def guilds(self, ctx):
        await ctx.reply(f"I am currently in **{len(self.bot.guilds)}** guilds!")



    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def invite(self, ctx, guild : discord.Guild):
        invite = await guild.text_channels[0].create_invite(max_uses = 1, reason = "Invite requested by the bot owner")
        await ctx.reply(invite.url)



def setup(bot):
    bot.add_cog(Owner(bot))   
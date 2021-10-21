import discord
import datetime, time
import json
from discord import activity

from discord.ext import commands
from discord_components import *


class Info_Handler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def save_json(self):
        with open("data/prefixes.json", "w") as f:
            json.dump(prefixes, f)
        

    @commands.Cog.listener("on_ready")
    async def _on_ready(self):
        global startTime
        startTime = round(time.time())

        DiscordComponents(self.bot)
        
        print("Bot is ready!")
        

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def uptime(self, ctx):
        uptime = str(datetime.timedelta(seconds = int(round(time.time() - startTime))))
        await ctx.send(f"Uptime: {uptime}")

    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def prefix(self, ctx, newPrefix = None):
        if newPrefix:
            self.bot.command_prefix = prefixes[str(ctx.channel.guild.id)] = newPrefix

            self.save_json()

            await ctx.send("The new prefix is `{}`".format(newPrefix))
        else:
            await ctx.send("The prefix is `{}`".format(prefixes[str(ctx.channel.guild.id)]))

    
    @commands.command(aliases = ['v'])
    @commands.has_permissions(administrator = True)
    async def version(self, ctx):
        await ctx.send(f"The Bot runs on version **{4.0}**")


with open('data/prefixes.json') as file:
    prefixes = json.load(file)
    file.close()


def setup(bot):
    bot.add_cog(Info_Handler(bot))
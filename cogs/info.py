import discord
import datetime, time
import json
from discord import activity

from discord.ext import commands
from discord_components import *


class Info_Handler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


        with open('data/prefixes.json') as file:
            self.prefixes = json.load(file)
            file.close()

    def save_json(self):
        with open("data/prefixes.json", "w") as f:
            json.dump(self.prefixes, f)
        

    @commands.Cog.listener("on_ready")
    async def _on_ready(self):

        DiscordComponents(self.bot)
        print("Bot is ready!")
        
    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def prefix(self, ctx, newPrefix = None):
        if newPrefix:
            self.bot.command_prefix = self.prefixes[str(ctx.channel.guild.id)] = newPrefix

            self.save_json()

            await ctx.send("The new prefix is `{}`".format(newPrefix))
        else:
            await ctx.send("The prefix is `{}`".format(self.prefixes[str(ctx.channel.guild.id)]))






def setup(bot):
    bot.add_cog(Info_Handler(bot))
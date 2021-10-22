from os import error
import discord
import json
import re

from enum import Enum
from discord.ext import commands

from cogs.__classes.settings import *


class InfoHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    
    def save_json(self, settings):
        with open("data/settings.json", "w") as f:
            json.dump(settings, f)

    def open_json(self):
        with open('data/settings.json') as file:
            settings = json.load(file)
            file.close()

        return settings

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def add_suggestions_channel(self, ctx, channel : discord.TextChannel):
        
        guild_id = str(ctx.channel.guild.id)
        settings = self.open_json()

        if channel.id not in settings[guild_id][Settings.suggestions_channels.value]:
            settings[guild_id][Settings.suggestions_channels.value].append(channel.id)

            self.save_json()
            await ctx.send("<#{}> added to the suggestions channels!".format(channel.id))
        else:
            await ctx.send("This channel is already a suggestion channel!")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def remove_suggestions_channel(self, ctx, channel : discord.TextChannel):
        
        guild_id = str(ctx.channel.guild.id)
        settings = self.open_json()

        if channel.id in settings[guild_id][Settings.suggestions_channels.value]:
            settings[guild_id][Settings.suggestions_channels.value].remove(channel.id)

            self.save_json()
            await ctx.send("<#{}> removed from the suggestions channels!".format(channel.id))
        else:
            await ctx.send("This channel is not a suggestion channel!")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_suggestion_channels(self, ctx, channel : discord.TextChannel):
        
        guild_id = str(ctx.channel.guild.id)
        settings = self.open_json()

        message = ""

        for channel in settings[guild_id][Settings.suggestions_channels.value]:
            message += f"<#{channel}> ; "

        if message != "":
            message = message[:-1]
        else:
            message = "There are no suggestions channels!"

        await ctx.send(message)


    @commands.Cog.listener("on_message")
    async def suggestions_listener(self, message):

        if isinstance(message.channel, discord.DMChannel):
            return

        try:

            guild_id = str(message.guild.id)
            settings = self.open_json()

            if settings[guild_id]:

                suggestions_channels = settings[guild_id][Settings.suggestions_channels.value]

                hasLinkRepost = re.search("/channels/", message.content, re.IGNORECASE)

                for suggestions_channel in suggestions_channels:
                    if message.channel.id == suggestions_channel and (message.reference is not None or hasLinkRepost):
                        user = message.author
                        content = message.content

                        await message.delete()

                        await user.send(f"**Your message was deleted in <#{suggestions_channel}> because it was detected as a possible repost**\n **Message content:** {content}")
                        
                        if message.reference is not None:

                            originalMessage = await message.channel.fetch_message(message.reference.message_id)
                            originalUser = originalMessage.author
                            
                            if originalUser is not user:
                                await originalUser.send(f"**<@{user.id}> replied to your message.\nYour message:** {originalMessage.jump_url}\n**Their message:** {content}")
        except:
            pass

def setup(bot):
    bot.add_cog(InfoHandler(bot))
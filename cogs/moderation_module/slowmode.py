import discord
import json

from discord import channel
from discord.ext import commands

from cogs.__classes.settings import *


class Slowmode_Module(commands.Cog):

    def __init__ (self, bot):
        self.bot = bot


    @commands.command(aliases = ['getsc'])
    @commands.has_permissions(administrator = True)
    async def getslowmodechannels(self, ctx):
        guild_id = str(ctx.channel.guild.id)

        channels = settings[guild_id][Settings.slowmode_channels.value]

        finalMessage = ""

        for channel in channels:
            message = "**Channel:** <#{}>\n**Default slowmode:** {} seconds\n\n".format(str(channel['id']), str(channel['default_slowmode']))
            finalMessage += message

        if finalMessage == "":
            finalMessage = "There are no slowmode channel set yet!"

        await ctx.send(finalMessage)

    
    @commands.command(aliases = ['gs'])
    @commands.has_permissions(administrator = True)
    async def globalslowmode(self, ctx, Type, seconds : int = 5):

        types = ["set", "add", "default"]

        Type = Type.lower()

        if Type not in types:
            await ctx.send("Make sure you follow the format: `(prefix)globalslowmode [Set / Add / Default] <Seconds>`")
            return

        guild_id = str(ctx.channel.guild.id)

        channels = settings[guild_id][Settings.slowmode_channels.value]

        channelsAfected = 0
        channelsAfected = int (channelsAfected)

        for channel in channels:
    
            actualChannel = self.bot.get_channel(channel['id'])

            currentSlowmode = actualChannel.slowmode_delay

            newSlowmode = 0
            newSlowmode = int (newSlowmode)

            message = "null"

            if Type == "default":
                newSlowmode = channel['default_slowmode'] 
                message = "Slowmode set to default"
            elif Type == "add":
                newSlowmode = currentSlowmode + seconds
                message = "Slowmode increased with {} seconds".format(seconds)
            elif Type == "set":
                newSlowmode = seconds
                message = "Slowmode set to {} seconds".format(seconds)
            
            await actualChannel.edit(slowmode_delay = newSlowmode)
            channelsAfected += 1

        await ctx.send("{} for {} channels!".format(message, channelsAfected))

    @commands.command(name = "Slowmode", aliases = ['sc'])
    @commands.has_permissions(administrator = True)
    async def slowmodechannel(self, ctx, Type, channel : discord.TextChannel, default_slowmode = 5):

        types = ["add", "remove", "change"]

        Type = Type.lower()

        if Type not in types:
            await ctx.send("Make sure you follow the format: `slowmodechannel [Add / Remove / Change] [Channel] <Slowmode>`")
            return

        channelDict = {
            "id" : channel.id,
            "default_slowmode" : default_slowmode
        }

        message = ""

        guild_id = str(ctx.channel.guild.id)


        if Type == "add":
            if channelDict not in settings[guild_id][Settings.slowmode_channels.value]:
                settings[guild_id][Settings.slowmode_channels.value].append(channelDict)
                message = "<#{}> added with `default_slowmode = {}`".format(channel.id, default_slowmode)
            else:
                message = "This channel is already added! Use `slowmodechannel change` to edit this channel's settings!"

        
        elif Type == "remove":
            dictLen = len(settings[guild_id][Settings.slowmode_channels.value])
            found = False

            for i in range(0, dictLen):
                if settings[guild_id][Settings.slowmode_channels.value][i]['id'] == channel.id:
                    del settings[guild_id][Settings.slowmode_channels.value][i]
                    message = "<#{}> removed!".format(channel.id)
                    found = True
                    break

            if not found:
                message = "This channel doesn't have a default slowmode! Use `{}slowmodechannel add` to add the channel!"

        elif Type == "change":
            dictLen = len(settings[guild_id][Settings.slowmode_channels.value])
            found = False

            for i in range(0, dictLen):
                if settings[guild_id][Settings.slowmode_channels.value][i]['id'] == channel.id:
                    settings[guild_id][Settings.slowmode_channels.value][i]['default_slowmode'] = default_slowmode 
                    message = "Default slowmode was changed for <#{}> to {}!".format(channel.id, default_slowmode)
                    found = True
                    break
                    
            if not found:
                message = "This channel doesn't have a default slowmode! Use `{}slowmodechannel add` to add the channel!"
            

        with open("data/settings.json", "w") as f:
            json.dump(settings, f)

        await ctx.send(message)
    
    @slowmodechannel.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Make sure you follow the format: `slowmodechannel [Add / Remove / Change] [Channel] <Slowmode>`")


    @globalslowmode.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Make sure you follow the format: `globalslowmode [Set / Add / Default] <Seconds>`")


class Channel():
    def __init__(self, id, default_slowmode):
        self.id = id
        self.default_slowmode = default_slowmode


with open('data/settings.json') as settingsFile:
    settings = json.load(settingsFile)
    settingsFile.close()

def setup(bot):
    bot.add_cog(Slowmode_Module(bot))
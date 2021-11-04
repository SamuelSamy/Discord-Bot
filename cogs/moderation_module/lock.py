import discord
import json
import typing

from discord.colour import Color
from discord.ext import commands
from discord.utils import get
from discord import CategoryChannel

from cogs.__classes.settings import * 


class Lock_Module(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.lock_role = 903399550889361428

    @commands.command()
    @commands.has_permissions(manage_channels = True)
    async def lock(self, ctx, channel : typing.Optional[discord.TextChannel], *, message = ""):

        user = ctx.message.author
        guild = ctx.message.guild
        role = guild.get_role(self.lock_role)

        if user.guild_permissions.administrator or role in user.roles:

            channel = channel or ctx.channel
            guild_id = str(ctx.channel.guild.id)
            role = get(ctx.guild.roles, id = settings[guild_id][Settings.lock_role.value])
            
            permission_value = 1
            permissions = channel.overwrites_for(role)

            if permissions.pair()[1].value & (1 << 11):
                permission_value = -1

            permissions.update(send_messages = False)

            if permission_value != -1:
                await channel.set_permissions(role, overwrite = permissions)

                embedVar = discord.Embed(title = "🔒 Channel Locked", description = message, color = 0xFF0000)
                await channel.send(embed = embedVar)

                if channel != ctx.channel:
                    await ctx.send("<#{}> is now locked!".format(channel.id))
            else:
                if channel != ctx.channel:
                    await ctx.send("<#{}> is already locked!".format(channel.id))
                else:
                    await ctx.send("This channel is already locked!")


    @commands.command()
    @commands.has_permissions(manage_channels = True)
    async def unlock(self, ctx, channel : typing.Optional[discord.TextChannel], *, message = ""):

        user = ctx.message.author
        guild = ctx.message.guild
        role = guild.get_role(self.lock_role)

        if user.guild_permissions.administrator or role in user.roles:

            channel = channel or ctx.channel
            guild_id = str(ctx.channel.guild.id)

            role = get(ctx.guild.roles, id = settings[guild_id][Settings.lock_role.value])

            permission_value = 1
            permissions = channel.overwrites_for(role)
            
            if permissions.pair()[1].value & (1 << 11):
                permission_value = -1

            permissions.update(send_messages = None)

            if permission_value == -1:
                await channel.set_permissions(role, overwrite = permissions)

                embedVar = discord.Embed(title = "🔓 Channel Unlocked", description = message, color = 0x00FF00)
                await channel.send(embed = embedVar)

                if channel != ctx.channel:
                    await ctx.send("<#{}> is no longer locked!".format(channel.id))
            else:
                if channel != ctx.channel:
                    await ctx.send("<#{}> is not locked!".format(channel.id))
                else:
                    await ctx.send("This channel is not locked!")
    

    @commands.command()
    @commands.has_permissions(manage_channels = True)
    async def lockdown(self, ctx, Type, *, message = ""):
        
        user = ctx.message.author
        guild = ctx.message.guild
        role = guild.get_role(self.lock_role)

        if user.guild_permissions.administrator or role in user.roles:

            guild_id = str(ctx.channel.guild.id)
            role = get(ctx.guild.roles, id = settings[guild_id][Settings.lock_role.value])

            channels = settings[guild_id][Settings.lockdown_channels.value]

            Type = Type.lower().strip()
            send_message = None
            _title = "🔓 Channel Unlocked"
            _color = 0x00FF00
            _response = "Unlocking"
            
            if Type == "enable":
                send_message = False
                _title = "🔒 Channel Locked"
                _color = 0xFF0000
                _response = "Locking"
            elif Type != "disable":
                return

            totalChannels = int(0)

            inititalMessage: discord.TextChannel.Message = None

            if Type == "enable":
                inititalMessage = await ctx.send(f"Locking Channels...\n0/{len(channels)}")
            else:
                inititalMessage = await ctx.send(f"Unlocking Channels...\n0/{len(channels)}")

            for channelId in channels:
                channel = self.bot.get_channel(channelId)
                permissions = channel.overwrites_for(role)

                if Type == "enable":
                    permissions.update(send_messages = False)
                else:
                    permissions.update(send_messages = None)

                await channel.set_permissions(role, overwrite = permissions)

                embedVar = discord.Embed(title = _title, description = message, color = _color)
                await channel.send(embed = embedVar)
                totalChannels += 1

                await inititalMessage.edit(content = f"{_response} Channels...\n{totalChannels}/{len(channels)}")
            
            await inititalMessage.edit(content = f"{totalChannels} Channels {_response[:-3]}ed!")


    @commands.command(aliases = ['lc'])
    @commands.has_permissions(administrator = True)
    async def lockdownchannel(self, ctx, Type, channel : discord.TextChannel):

        guild_id = str(ctx.channel.guild.id)

        types = ["add", "remove"]

        Type = Type.lower()

        if Type not in types:
            await ctx.send("Make sure you follow the format: `{}lockdownchannel [Add / Remove] [Channel]`".format(commands.Cog.command_prefix))
            return

        message = ""
    
        if Type == "add":
            if channel.id not in settings[guild_id][Settings.lockdown_channels.value]:
                settings[guild_id][Settings.lockdown_channels.value].append(channel.id)
                message = "<#{}> added to the lockdown list!".format(channel.id)
            else:
                message = "This channel is already added! Use `{}lockdownchannel remove` to remove this channel".format(commands.Cog.command_prefix)
        
        elif Type == "remove":
            dictLen = len(settings[guild_id][Settings.lockdown_channels.value])
            found = False

            for i in range(0, dictLen):
                if settings[guild_id][Settings.lockdown_channels.value][i] == channel.id:
                    del settings[guild_id][Settings.lockdown_channels.value][i]
                    message = "<#{}> removed!".format(channel.id)
                    found = True
                    break

            if not found:
                message = "This channel is not on the lockdown list! Use `{}lockdownchannel add` to add the channel!"

        with open("data/settings.json", "w") as f:
            json.dump(settings, f)

        await ctx.send(message)
    

    @commands.command(aliases = ['getlc'])
    @commands.has_permissions(administrator = True)
    async def getlockdownchannels(self, ctx):
        guild_id = str(ctx.channel.guild.id)

        channels = settings[guild_id][Settings.lockdown_channels.value]

        finalMessage = "**Channels:**\n"

        for channelId in channels:
            message = "<#{}>  ;  ".format(channelId)
            finalMessage += message

        await ctx.send(finalMessage)


    @lockdownchannel.error
    async def slowmode_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Make sure you follow the format: `{}lockdownchannel [Add / Remove] [Channel]`".format(commands.Cog.command_prefix))


    @lockdown.error
    async def lockdown_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Make sure you follow the format: `{}lockdown [Enable / Disable] <Optional Message>`".format(self.bot.command_prefix))


async def check_permission(channel : discord.TextChannel, role, permission_value):
    perms = channel.overwrites_for(role)

    allowed = perms.pair()[0].value
    denied = perms.pair()[1].value

    if denied & permission_value:
        return -1
    elif allowed & permission_value:
        return 1

    return 0


with open('data/settings.json') as file:
    settings = json.load(file)
    file.close()


def setup(bot):
    bot.add_cog(Lock_Module(bot))
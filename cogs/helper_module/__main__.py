import time
import typing
import discord
import json
import re

from discord import channel
from discord.ext import commands
from discord.utils import get

from cogs.__classes.settings import *


class Helper_Listener(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


    def save_json(self):
        with open("data/settings.json", "w") as f:
            json.dump(settings, f)


    def generate_embed_message_delete(self, user, message):

        embed = discord.Embed(
            color = 0xe74c3c,
            description = f"Message from <@{message.author.id}> deleted by <@{user.id}> in <#{message.channel.id}>\nIt was sent on <t:{round(message.created_at.timestamp())}>\nIt was deleted on <t:{round(time.time())}>"
        )

        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )

        if message.content:
            embed.add_field(
                name = "Message Content",
                value = message.content,
                inline = False
            )    

        if message.attachments:
            embed.set_image(
                url = message.attachments[0].proxy_url
            )

        embed.set_footer(
            text = f"User ID:   {message.author.id}\nHelper ID: {user.id}"
        )

        return embed
    
    def generate_empty_embed_for_attachment(self, user, message, attachment):

        embed = discord.Embed(
            color = 0xe74c3c,
            description = f"Message from <@{message.author.id}> deleted by <@{user.id}> in <#{message.channel.id}> \nIt was sent on <t:{round(message.created_at.timestamp())}>\nIt was deleted on <t:{round(time.time())}>"
        )

        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )

        embed.set_image(
            url = attachment.proxy_url
        )

        embed.set_footer(
            text = f"User ID:   {message.author.id}\nHelper ID: {user.id}"
        )

        return embed

    def generate_embed_nick_changed(self, user, before, after):
        
        embed = discord.Embed(
            color = 0xffa500,
            description = f"The nickname for <@{after.id}> was changed by <@{user.id}> at <t:{round(time.time())}>"
        )

        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )

        embed.add_field(
            name = "Before",
            value = before.nick,
            inline = True
        )    

        embed.add_field(
            name = "After",
            value = after.nick,
            inline = True
        )    

 
        embed.set_footer(
            text = f"User ID:   {before.id}\nHelper ID: {user.id}"
        )

        return embed


    @commands.Cog.listener()
    async def on_message_delete(self, message):

        try:
            if not isinstance(message.channel, discord.DMChannel):   

                guild = message.guild
                guild_id = str(guild.id)

                try:

                    if settings[guild_id]:
                        
                        log_channel = self.bot.get_channel(settings[guild_id][Settings.helper_logs.value])
                        helper_role = guild.get_role(settings[guild_id][Settings.helper_role.value])

                        fetched_logs = await guild.audit_logs(limit = 1).flatten()

                        if fetched_logs:
                            log = fetched_logs[0]
                            if  helper_role in log.user.roles:    
                                if log.extra.channel.id == message.channel.id:
                                    if log.user.id != message.author.id:

                                        await log_channel.send(embed = self.generate_embed_message_delete(log.user, message))
                                        
                                        if len(message.attachments) > 1:
                                            for i in range(1, len(message.attachments)):
                                                await log_channel.send(embed = self.generate_empty_embed_for_attachment(log.user, message, message.attachments[i]))
                except:
                    print("Error on messge_delete (helper)")
        except:
            print("Error on messge_delete (helper)")

            
    @commands.Cog.listener("on_member_update")
    async def helper_listener(self, before, after):
        
        try:

            if before.nick != after.nick:

                guild = after.guild
                guild_id = str(guild.id)

                log_channel = self.bot.get_channel(settings[guild_id][Settings.helper_logs.value])
                helper_role = guild.get_role(settings[guild_id][Settings.helper_role.value])

                fetched_logs = await guild.audit_logs(limit = 1, action = discord.AuditLogAction.member_update).flatten()

                if fetched_logs:
                    log = fetched_logs[0]

                    if  helper_role in log.user.roles:    
                        if log.user.id != after.id:
                                await log_channel.send(embed = self.generate_embed_nick_changed(log.user, before, after))
        except:
            print ("Mimber Update error - Helper")
    


    @commands.Cog.listener("on_member_update")
    async def member_update(self, before, after):
        
        try:
            guild = after.guild
            guild_id = str(guild.id)

            helper_role_id = settings[guild_id][Settings.helper_role.value]
            helper_role = guild.get_role(helper_role_id)

            if helper_role in after.roles and helper_role not in before.roles:
                settings[guild_id][Settings.helpers.value].append(after.id)
            elif helper_role in before.roles and helper_role not in after.roles and after.id in settings[guild_id][Settings.helpers.value]:
                settings[guild_id][Settings.helpers.value].remove(after.id)


            self.save_json()
        except:
            print ("Member update error - Helper")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_helpers(self, ctx):
        
        helpers = "The following users are helpers:\n"
        guild_id = str(ctx.channel.guild.id)

        for helper_id in settings[guild_id][Settings.helpers.value]:
            helpers += f"• <@{helper_id}>\n"    

        if helpers == "The following users are helpers:\n":
            helpers = "There are no helpers!"

        await ctx.send(helpers)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def set_helper_log_channel(self, ctx, channel : typing.Optional[discord.TextChannel]):
        
        if channel == None:
            channel = ctx.channel

        guild_id = str(ctx.channel.guild.id)

        settings[guild_id][Settings.helper_logs.value] = channel.id
        self.save_json()

        await ctx.send(f"<#{channel.id}> is now the helper logging channel")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def set_helper_role(self, ctx, role : typing.Optional[discord.Role]):
        
        if role:
            members = role.members

            guild_id = str(ctx.channel.guild.id)

            old_helpers = len(settings[guild_id][Settings.helpers.value])
            new_helpers = len(members)

            settings[guild_id][Settings.helpers.value].clear()


            for member in members:
                settings[guild_id][Settings.helpers.value].append(member.id)

            settings[guild_id][Settings.helper_role.value] = role.id
            self.save_json()

            await ctx.send(f"<@&{role.id}> is now the helper role!\n> {old_helpers} helpers were removed\n> {new_helpers} helpers were added")
        else:
            await ctx.send("Please provide a role")



with open('data/settings.json') as settingsFile:
    settings = json.load(settingsFile)
    settingsFile.close()


def setup(bot):
    bot.add_cog(Helper_Listener(bot))   
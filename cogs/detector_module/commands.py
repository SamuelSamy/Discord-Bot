import discord
import json
import re


from discord.ext import commands
from discord.utils import get

from cogs.detector_module.package_functions import *


class Detector_Module_Commands(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


        with open('data/blacklist.json') as file:
            self.blacklisted = json.load(file)
            file.close()


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def add_blacklist(self, ctx, *, message : str):
        
        if ctx.author.id == 225629057172111362:
            if message not in self.blacklisted['scam_domains']:
                self.blacklisted['scam_domains'].append(message)
                save_json(self.blacklisted)
                await ctx.send(f"self.blacklisted: {message}")
            else:
                await ctx.send(f"`{message}` is already self.blacklisted")
            

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_blacklist(self, ctx):
        
        c_links = 0
        message = "```\n"

        for link in self.blacklisted['scam_domains']:

            c_links += 1
            
            message += f"• {link}\n"

            if c_links % 20 == 0 :
                await ctx.send(f"{message}\n```")
                message = "```\n"

        if c_links != 0 and message != "":
            await ctx.send(f"{message}\n```")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def add_mask(self, ctx, message : str, value : int):
        
        if ctx.author.id == 225629057172111362:
            if message not in self.blacklisted['masks']:
                self.blacklisted['masks'][message] = value
                save_json(self.blacklisted)
                await ctx.send(f"Added mask: `{message}`\nDistance: {value}")
            else:
                await ctx.send(f"`{message}`` is already self.blacklisted")
            

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_masks(self, ctx):
        
        message = "```py\n"    

        for mask in self.blacklisted['masks']:
            distance = self.blacklisted['masks'][mask]['distance']
            message += f"• {mask} ({distance})\n"

        await ctx.send(f"{message}```")
    

    # @commands.command()
    # @commands.has_permissions(administrator = True)
    # async def check(self, ctx, *, message : str):
        
    #     if is_self.blacklisted(message):
    #         await ctx.send("This link is self.blacklisted")
    #     else:
    #         value = is_mask(message, self.blacklisted)
    #         await ctx.send(f"Levenshtein Distance: {value}")


    # @commands.command()
    # @commands.has_permissions(administrator = True)
    # async def check_by_id(self, ctx, channel_id, message_id):

    #     channel = self.bot.get_channel(int(channel_id))
    #     message = await channel.fetch_message(int(message_id))
    #     message = message.content.replace('\x00', '')

    #     if is_self.blacklisted(message):
    #         await ctx.send("This link is self.blacklisted")
    #     else:
    #         value = is_mask(message, self.blacklisted)
    #         await ctx.send(f"Levenshtein Distance: {value}")





def setup(bot):
    bot.add_cog(Detector_Module_Commands(bot))   
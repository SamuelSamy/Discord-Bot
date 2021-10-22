import discord
import json
import re


from discord.ext import commands
from discord.utils import get

from cogs.__classes.settings import * 


class Detector_Module_Commands(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


    def save_json(self):
        with open("data/blacklist.json", "w") as f:
            json.dump(blacklisted, f)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def check(self, ctx, *, message : str):
        
        if self.is_blacklisted(message):
            await ctx.send("This link is blacklisted")
        elif self.is_possible_scam(message):
            await ctx.send("This link is not blacklisted but it is a possible scam link")
        else:
            await ctx.send("This link is not blacklisted and it is not detected as a scam link")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def add_blacklist(self, ctx, *, message : str):
        
        if ctx.author.id == 225629057172111362:
            if message not in blacklisted['scam_links']:
                blacklisted['scam_links'].append(message)
                self.save_json()
                await ctx.send(f"Blacklisted: {message}")
            else:
                await ctx.send(f"`{message}` is already blacklisted")
            

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_blacklist(self, ctx):
        
        c_links = 0
        message = "```\n"

        for link in blacklisted['scam_links']:

            c_links += 1
            
            message += f"• {link}\n"

            if c_links % 20 == 0 :
                await ctx.send(message)
                message = "```\n"

        if c_links != 0 and message != "":
            await ctx.send(f"{message}```")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def add_mask(self, ctx, message : str, value : int):
        
        if ctx.author.id == 225629057172111362:
            if message not in blacklisted['masks']:
                blacklisted['masks'][message] = value
                self.save_json()
                await ctx.send(f"Added mask: `{message}`\nDistance: {value}")
            else:
                await ctx.send(f"`{message}`` is already blacklisted")
            

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_masks(self, ctx):
        
        message = "```py\n"    

        for mask in blacklisted['masks']:
            value = blacklisted['masks'][mask]
            message += f"• {mask} ({value})\n"

        await ctx.send(f"{message}```")
  

with open('data/blacklist.json') as file:
    blacklisted = json.load(file)
    file.close()


def setup(bot):
    bot.add_cog(Detector_Module_Commands(bot))   
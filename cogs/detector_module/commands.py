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


    def get_first_part(self, message):
        link = re.search("(?P<url>https?://[^\s]+)", message)
        return link[0]


    def reassmble_link(self, parts):
        link = ""

        for i in range(2, len(parts)):
            link += parts[i] + "/"

        return link[:-1]


    def is_blacklisted(self, message):
        links_in_message = re.findall("(?P<url>https?://[^\s]+)", message)

        for link in links_in_message:
            link_parts = link.split('/')

            if len(link_parts) > 2:
                to_verrify = self.reassmble_link(link_parts)

                if to_verrify in blacklisted['scam_links']:
                    return True

        return False


    def is_possible_scam(self, message):

        links_in_message = re.findall("(?P<url>https?://[^\s]+)", message)

        masks = []
        for mask in blacklisted['masks']:
            masks.append(masks)

        for link in links_in_message:
            link_parts = link.split('/')

            if len(link_parts) > 2:
                to_verrify = link_parts[2]
                
                for mask in masks:
                    
                    distance = self.levenshtein_distance(to_verrify, mask)
                    
                    if distance > 0 and distance < 4 and to_verrify not in masks:
                        return True

        return False


    def levenshtein_distance(self, s, t):
        # https://www.datacamp.com/community/tutorials/fuzzy-string-python?utm_source=adwords_ppc&utm_campaignid=14989519638&utm_adgroupid=127836677279&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=332602034364&utm_targetid=dsa-429603003980&utm_loc_interest_ms=&utm_loc_physical_ms=9040263&gclid=CjwKCAjwwsmLBhACEiwANq-tXHKieLemSgdCcH-veD1PhSOzUHK06Hp2e0PcefOtwX7-w_yh8FCHlRoCq4kQAvD_BwE
        rows = len(s)+1
        cols = len(t)+1
        
        distance = []
        
        for i in range(0, rows):

            row = []

            for j in range(0, cols):
                row.append(0)

            distance.append(row) 


        for i in range(1, rows):
            for k in range(1,cols):
                distance[i][0] = i
                distance[0][k] = k

        for col in range(1, cols):
            for row in range(1, rows):
                if s[row-1] == t[col-1]:
                    cost = 0 
                else:
                    cost = 1

                distance[row][col] = min(
                    distance[row-1][col] + 1,  
                    distance[row][col-1] + 1,          
                    distance[row-1][col-1] + cost
                )    
        
        return distance[row][col]

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
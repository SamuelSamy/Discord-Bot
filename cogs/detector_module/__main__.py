import discord
import json
import re


from discord.ext import commands
from discord.utils import get

from cogs.__classes.settings import * 


class Detector_Module(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


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
        mask = "discord.gift"

        links_in_message = re.findall("(?P<url>https?://[^\s]+)", message)

        for link in links_in_message:
            link_parts = link.split('/')

            if len(link_parts) > 2:
                to_verrify = link_parts[2]
                
                distance = self.levenshtein_distance(to_verrify, mask)

                if distance > 0 and distance < 4:
                    return True

        return False

    
    async def send_to_logs(self, message):
        member = message.author
        guild = str(message.guild.id)
        
        mod_logs = self.bot.get_channel(settings[guild][Settings.mod_logs.value])


        embed = discord.Embed(color = 0xf04848)
        embed.set_author(name = f"[Kick] {member}", icon_url = member.avatar_url)
        embed.add_field(name = "User", value = member.mention)
        embed.add_field(name = "Moderator", value = self.bot.user.mention)
        embed.add_field(name = "Reason", value = "Compromised Account")
    
        await member.send(f"Hello {member.mention}\nYou were kicked from {message.guild} because your account was recentlly ")

        await mod_logs.send(embed = embed)


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


    @commands.Cog.listener("on_message")
    async def scam_listener(self, message):

        
        member = message.author

        if not (message.author.id == self.bot.user.id or isinstance(message.channel, discord.DMChannel) or message.content is None or type(member) != discord.Member):
            
            guild = str(message.guild.id)

            if not (member.guild_permissions.administrator or member.bot):
                
                try:

                    has_link = re.search("https?://", message.content, re.IGNORECASE)

                    if has_link:

                        if self.is_blacklisted(message.content):

                            await message.delete()

                            scam_logs = self.bot.get_channel(settings[guild][Settings.scam_logs.value])
                            await scam_logs.send(f"``` ```\n**Message sent by**: {message.author.mention}\n**Content:**\n```\n`{message.content}`\n```")
                            
                            await self.send_to_logs()

                            await member.kick("Compromised Account")

                        elif self.is_possible_scam(message.content):

                            await message.delete()

                            scam_logs = self.bot.get_channel(settings[guild][Settings.scam_logs.value])
                            await scam_logs.send(f"``` ```\n**<@225629057172111362> THIS LINK IS NOT BLACKLISTED!**\n**Message sent by**: {message.author.mention}\n**Content:**\n```\n`{message.content}`\n```")
                            
                            await self.send_to_logs()

                            await member.kick("Compromised Account")
                
                except:
                    print ("Error - Scam Listner")


                

with open('data/blacklist.json') as file:
    blacklisted = json.load(file)
    file.close()


with open('data/settings.json') as file:
    settings = json.load(file)
    file.close()

def setup(bot):
    bot.add_cog(Detector_Module(bot))   
from os import error
import discord
import json
import re
from discord.channel import CategoryChannel


from discord.ext import commands
from discord.utils import get

from cogs.__classes.settings import Settings
from cogs.detector_module.package_functions import *


class Detector_Module(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot


    @commands.Cog.listener("on_message")
    async def scam_listener(self, message):

        try:

            member = message.author

            if  not (message.author.id == self.bot.user.id or isinstance(message.channel, discord.DMChannel) \
                or message.content is None or type(member) != discord.Member):
                
                guild = str(message.guild.id)

                if not (member.guild_permissions.administrator or member.bot):

                    try:
                        
                        message_content = message.content.replace('\x00', '')
                        has_link = re.search("https?://", message_content, re.IGNORECASE)

                        on_blacklist = is_blacklisted(message_content, blacklisted)

                        if on_blacklist or (has_link and is_mask(message_content, blacklisted)) or is_possible_scam(message_content):
                            
                            try:
                                await message.delete()
                            except:
                                print ("Message already deleted")

                            scam_logs = self.bot.get_channel(settings[guild][Settings.scam_logs.value])
                            await scam_logs.send(f"``` ```\n**Message sent by**: {message.author.mention}\n**Content:**\n```\n{message_content}\n```")
                            
                            await send_to_mod_logs(self, message, settings)

                            await member.kick(reason = "Compromised Account")

                            if not on_blacklist:
                                await send_link_to_logs(self, message_content)
                            
                    except: 
                        print ("Error - Scam Lisnter")
        except:
            print ("Error - Scam Lisnter")


with open('data/blacklist.json') as file:
    blacklisted = json.load(file)
    file.close()


with open('data/settings.json') as file:
    settings = json.load(file)
    file.close()


def setup(bot):
    bot.add_cog(Detector_Module(bot))   
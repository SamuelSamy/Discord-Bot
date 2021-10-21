import asyncio
import discord
import json
import math

from discord import channel
from discord.ext import commands

class MmebersModule(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_members(self, ctx, role : discord.Role):

        members = role.members
        maxMembersInMessage = int(25)

        currentPage = 0
        pages =  math.ceil(len (members) / maxMembersInMessage)

        currentMessage = f"``` Page {currentPage + 1} / {pages} ```\n"
        currentMessageId = 0

        for member in members:
            currentMessage += f"○ {member.mention}\n"
            currentMessageId += 1

            if currentMessageId % maxMembersInMessage == 0:

                await ctx.send(currentMessage)

                currentPage += 1
                currentMessage = f"``` Page {currentPage + 1} / {pages} ```\n"

                await asyncio.sleep(1)

        await ctx.send(currentMessage)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def get_members_ids(self, ctx, role : discord.Role):

        members = role.members
        maxMembersInMessage = int(25)

        currentPage = 0
        pages = math.ceil(len (members) / maxMembersInMessage)

        currentMessage = f"```Page {currentPage + 1} / {pages} ```\n ```\n"
        currentMessageId = 0
        
        for member in members:
            currentMessage += f"{member.id}\n"
            currentMessageId += 1

            if currentMessageId % maxMembersInMessage == 0:
                currentMessage += "```"

                await ctx.send(currentMessage)
                
                currentPage += 1
                currentMessage = f"```Page {currentPage + 1} / {pages} ```\n ```\n"
                
                await asyncio.sleep(1)
                
        currentMessage += "```"
        
        await ctx.send(currentMessage)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_reaction_members(self, ctx, channel : discord.TextChannel, messageID):
        message = await channel.fetch_message(messageID)

        reactions = message.reactions[0]

        members = await reactions.users().flatten()

        maxMembersInMessage = int(25)

        currentPage = 0
        pages =  math.ceil(len (members) / maxMembersInMessage)

        currentMessage = f"``` Page {currentPage + 1} / {pages} ```\n"
        currentMessageId = 0

        for member in members:
            currentMessage += f"○ {member.mention}\n"
            currentMessageId += 1

            if currentMessageId % maxMembersInMessage == 0:

                await ctx.send(currentMessage)

                currentPage += 1
                currentMessage = f"``` Page {currentPage + 1} / {pages} ```\n"

                await asyncio.sleep(1)

        await ctx.send(currentMessage)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_reaction_members_ids(self, ctx, channel : discord.TextChannel, messageID):
        message = await channel.fetch_message(messageID)

        reactions = message.reactions[0]

        members = await reactions.users().flatten()

        maxMembersInMessage = int(25)

        currentPage = 0
        pages = math.ceil(len (members) / maxMembersInMessage)

        currentMessage = f"```Page {currentPage + 1} / {pages} ```\n ```\n"
        currentMessageId = 0
        
        for member in members:
            currentMessage += f"{member.id}\n"
            currentMessageId += 1

            if currentMessageId % maxMembersInMessage == 0:
                currentMessage += "```"

                await ctx.send(currentMessage)
                
                currentPage += 1
                currentMessage = f"```Page {currentPage + 1} / {pages} ```\n ```\n"
                
                await asyncio.sleep(1)
                
        currentMessage += "```"
        
        await ctx.send(currentMessage)


def setup(bot):
    bot.add_cog(MmebersModule(bot))
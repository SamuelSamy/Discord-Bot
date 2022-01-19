import typing
import discord

from discord.ext import commands
from discord_components import *

from cogs.appeal_module.rewrite.package_functions import *


class Appeals(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_message(self, ctx, channel : typing.Optional[discord.TextChannel]):

        if channel is None:
            channel = ctx.channel
        
        embedVar = discord.Embed(
            title = "🟢 Ban Appeals", 
            description = "**Only submit an appeal request if you are banned from the game!**", 
            color = 0x20e848
        )

        instructions = f"> **•** Make sure your direct messages are **ON**!\n>  \n> **•** Press the `Appeal` button below.\n>  \n> **•** <@{self.bot.user.id}> will message you.\n>      Follow the instructions in order to submit your appeal!"

        embedVar.add_field(
            name = "How to appeal ❓", 
            value = instructions
        )

        embedVar.set_footer(
            text = "❗ Misusing the appeal system will result in a warn ❗"
        )

        comps = [
            Button (
                style = ButtonStyle.green,
                label = "Appeal",
                custom_id = "appeal_button",
            )
        ]

        await channel.send(
            embed = embedVar,
            components = comps
        )


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_cooldown(self, ctx, time):

        time_in_seconds = convert_time(time)
        guild = str(ctx.channel.guild.id)

        appeals = get_appeal_json()

        if time_in_seconds in [-1, -2]:
            await ctx.channel.send("Unable to change the cooldown")
        else:
            appeals[guild]['cooldown'] = time_in_seconds
            save_appeal_json(appeals)

            await ctx.channel.send(f"Cooldown set to {time}")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_channel(self, ctx, channel : typing.Optional[discord.TextChannel]):

        if channel is None:
            channel = ctx.channelf

        appeals = get_appeal_json()
        appeals[str(ctx.channel.guild.id)]['appeal_channel'] = channel.id
        save_appeal_json(appeals)
        await ctx.send(f"<#{channel.id}> set as the main appeal channel.")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_log_channel(self, ctx, channel : typing.Optional[discord.TextChannel]):

        if channel is None:
            channel = ctx.channel

        appeals = get_appeal_json()
        appeals[str(ctx.channel.guild.id)]['appeal_logs'] = channel.id
        save_appeal_json(appeals)
        await ctx.send(f"<#{channel.id}> set as the main appeals log channel.")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_appeal(self, ctx, id):

        try:
            id = int(id)
        except ValueError as ve:
            await ctx.channel.send("Unable to find appeal with specified id")

        if type(id) == int:
            
            appeal = get_appeal_by_id(ctx.guild.id, id)

            if appeal is not None:
                await ctx.channel.send(embed = generate_appeal(self.bot, ctx.channel.guild.id, appeal, False))
            else:
                await ctx.channel.send("Unable to find appeal with specified id")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_status(self, ctx, status):
        
        status = status.lower().strip()
        guild = ctx.guild

        appeals = get_appeal_json()
        
        if status in ["close", "false", "0"]:
            appeals[str(guild.id)]["accepting_appeals"] = False
            await ctx.send("Appeals are now clsoed")
        elif status in ["open", "true", "1"]:
            appeals[str(guild.id)]["accepting_appeals"] = False
            await ctx.send("Appeal are now open")
        else:
            await ctx.send("The status must be `close / false / 0` or `open / true / 1`")

        save_appeal_json(appeals)
       

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def logs(self, ctx, user : typing.Union[discord.User, int]):

        search_logs = True

        try:
            if isinstance(user, discord.User):
                id = user.id
            else:
                id = user
            
        except:
            await ctx.send("Invalid ID!\nMake sure you specify a **discord ID** or a **roblox ID**!")
            search_logs = False

        if search_logs:

            message = await ctx.send("Checking for logs...\nPlease wait!")
            logs = get_logs(ctx.channel.guild.id, id)

            if logs:
                await message.edit(logs)
            else:
                await message.edit("No logs found for this user!")


def setup(bot):
    bot.add_cog(Appeals(bot))
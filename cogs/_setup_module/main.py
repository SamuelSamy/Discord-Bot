import json
from math import e
from os import error
import re

from enum import Enum
from discord.ext import commands
from discord_components import *

class Settings(Enum):
    slowmode_channels    = 0 # []
    lockdown_channels    = 1 # []
    lock_role            = 2 # int
    scam_logs            = 3 # int
    mod_logs             = 4 # int
    muted_role           = 5 # int
    helpers              = 6 # []
    helper_logs          = 7 # int
    helper_role          = 8 # int
    suggestions_channels = 9 # []


class Setup_Module(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    
    def save_json(self):
        with open("data/settings.json", "w") as f:
            json.dump(settings, f)

        with open("data/appeals.json", "w") as f:
            json.dump(appeals, f)


    def server_is_already_setted_up(self, guild):
        
        for guild_setup in settings:
            if guild_setup == str(guild.id):
                return True

        return False


    def create_settings(self, guild):
        settings[str(guild.id)] = {}


    def create_settings_entry(self, guild, entry, value):
        settings[str(guild.id)][entry] = value


    def create_appeal(self, guild):
        appeals[str(guild.id)] = {
            "next_id": 0,
            "appeal_channel": 0,
            "appeal_logs": 0,
            "cooldown": 432000,
            "delete_time": 3600,
            "appeals": [],
            "sent_appeals": [],
            "handled_appeals": []
        }

    def change_appeal_entry(self, guild, entry, value):
        appeals[str(guild.id)][entry] = value


    def get_channels(self, message):

        channels = []

        matches = re.findall('<#\d+>', message)

        for match in matches:
            channel_id = str(match)[2:-1]

            if channel_id.isnumeric():
                channels.append(int(channel_id))

        return channels


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def setup(self, ctx):
        guild = ctx.channel.guild

        # TODO setup appeals

        if self.server_is_already_setted_up(guild):
            await ctx.send("This server is already setted up")
        else:

            self.create_settings(guild)
            self.create_appeal(guild)

            setup_steps = [
                "Mention the `muted` role",
                "Mention the `lockdown` role",
                "Mention the `helper` role",
                "Mention the `moderation logs` channel",
                "Mention the `scam logs` channel",
                "Mention the `global slowmode` channels",
                "Mention the `lockdown` channels",
                "Mention the `helper logs` channel",
                "Mention the `suggestions` channels",
                "Mention the `appeal` channel",
                "Mention the `appeal logs` channel"
            ]

            index = 0

            while index < len(setup_steps):
                
                await ctx.send(f"{setup_steps[index]}")


                message = await self.bot.wait_for(
                    'message',
                    check = lambda message: message.channel == ctx.channel and message.author == ctx.author
                )

                if index < 3:

                    role_id = message.content[3:-1]

                    try:
                        role_id = int(role_id)

                        if guild.get_role(role_id) is None:
                            await ctx.send("Role not found")
                            index -= 1
                        else:
                            sub_steps = {
                                0: Settings.muted_role.value,
                                1: Settings.lock_role.value,
                                2: Settings.helper_role.value
                            }   

                        self.create_settings_entry(guild, sub_steps[index], role_id)
                    except error:
                        print(error)
                        await ctx.send("Role not found")
                        index -= 1
                elif index < 9:
                    sub_steps = {
                        3: Settings.mod_logs.value,
                        4: Settings.scam_logs.value,
                        5: Settings.slowmode_channels.value,
                        6: Settings.lockdown_channels.value,
                        7: Settings.helper_logs.value,
                        8: Settings.suggestions_channels
                    }  

                    channels = self.get_channels(message.content)

                    if channels:

                        if index in [3, 4, 7]:
                            channels = channels[0]

                        self.create_settings_entry(guild, sub_steps[index], channels)
                    else:
                        await ctx.send("Error while processing the channels")    
                        index -= 1
                else:
                    sub_steps = {
                        9: 'appeal_channel',
                        10: 'appeal_logs'
                    }  

                    channel = message.content[2:-1]
                    if channel.isnumeric():
                        channel = int(channel)
                    
                        try:
                            channel_object = self.bot.get_channel(channel)

                            if channel_object:
                                self.change_appeal_entry(guild, sub_steps[index], channel)
                            else:
                                await ctx.send("Error while processing the channels")
                                index -= 1
                        except error:
                            print(error)
                            await ctx.send("Error while processing the channels")
                            index -= 1

                index += 1

            self.save_json()
            await ctx.send("Setup finished!")


with open('data/settings.json') as file:
    settings = json.load(file)
    file.close()


with open('data/appeals.json') as file:
    appeals = json.load(file)
    file.close()


def setup(bot):
    bot.add_cog(Setup_Module(bot))
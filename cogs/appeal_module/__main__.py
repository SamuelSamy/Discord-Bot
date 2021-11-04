from os import error
import time
import discord
import json
import typing
import urllib
import re

from enum import Enum
from discord.ext import commands, tasks
from discord.ext.commands import context
from discord_components import *


class Appeal(Enum):
    id              = 0
    created_at      = 1
    discord_id      = 2
    last_step       = 3
    roblox_link     = 4
    roblox_id       = 5
    ban_reason      = 6
    unban_reason    = 7
    response_time   = 8
    response        = 9


class Appeal_Module(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self.delete_appeals.start()


    def save_json(self):
        with open("data/appeals.json", "w") as f:
            json.dump(appeals, f)


    def convert_time(self, time):
        time_units = ['s', 'm', 'h', 'd']

        time_dict = {
            's' : 1,
            'm' : 60,
            'h' : 60 * 60,
            'd' : 60 * 60 * 24
        }

        time_unit = time[-1]

        if time_unit not in time_units:
            return -1

        try:
            actual_time = int(time[:-1])
        except:
            return -2
        
        return actual_time * time_dict[time_unit]
    

    def get_appeal_for_user(self, guild, id):

        for appeal in appeals[guild]['appeals']:
            if appeal[Appeal.discord_id.value] == id:
                return appeal

        return None

        
    def get_profile(self, name):

        link = f"https://www.roblox.com/User.aspx?Username={name}"

        try:

            opener = urllib.request.build_opener()
            request = urllib.request.Request(link)
            redirect = opener.open(request)
            profile = redirect.geturl()
    
            return profile

        except:
            return None

        
    def get_roblox_id(self, link):

        id = re.search("\d+", link)

        return id.group(0)


    def get_logs(self, guild, id):
        
        ids_list = []
        time_list = []
        answer_list = [] 

        for appeal in appeals[guild]['handled_appeals']:
            if appeal[Appeal.discord_id.value] == id or appeal[Appeal.roblox_id.value] == id:
                ids_list.append(appeal[Appeal.id.value])
                time_list.append(appeal[Appeal.response_time.value])
                answer_list.append(appeal[Appeal.response.value])

        deny = "<:redTick:897104673150996533>"
        accept = "<:greenTick:901197496276111451>"
        warn = "⚠️"
        
        actaul_string = ""

        for i in range(0, len(ids_list)):
            if answer_list[i] == 1:
                emoji = accept
            elif answer_list[i] == -1:
                emoji = deny
            else:
                emoji = warn

            actaul_string += f"{emoji} ID: {ids_list[i]} (<t:{time_list[i]}:R>)\n"

        
        return actaul_string    



    def generate_appeal(self, guild, appeal_message, prev_appeal = True):
        try:
            appeal_id = appeal_message[Appeal.id.value]

            sent_at = round(time.time())

            user_id = appeal_message[Appeal.discord_id.value]
            user = self.bot.get_user(user_id)

            roblox_link = appeal_message[Appeal.roblox_link.value]
            roblox_id = appeal_message[Appeal.roblox_id.value]

            ban_reason = appeal_message[Appeal.ban_reason.value]
            unban_reason = appeal_message[Appeal.unban_reason.value]

            embed = discord.Embed(
                color = 0x0f8adb
            )

            embed.set_author(
                name = f"{user}",
                icon_url = user.avatar_url
            )

            embed.add_field(
                name = "Discord Profile",
                value = f"{user.mention}  -  {user_id}",
                inline = False
            )    

            embed.add_field(
                name = "Roblox Profile",
                value = f"{roblox_link}  -  {roblox_id}",
                inline = False
            )                   
                    
        
            embed.add_field(
                name = "Why were you banned?",
                value = ban_reason,
                inline = False
            )

            embed.add_field(
                name = "Why do you think you should be unbanned?",
                value = unban_reason,
                inline = False
            )

            logs = ""
            _name = ""

            if prev_appeal:
                _name = "Previous Appeals"
                logs = self.get_logs(guild, user_id)
            else:
                _name = "Response"
                deny = "<:redTick:897104673150996533>"
                accept = "<:greenTick:897104713982541865>"
                warn = "⚠️"

                if appeal_message[Appeal.response.value] == 1:
                    logs = f"{accept} **ID: {appeal_message[Appeal.id.value]}** at <t:{appeal_message[Appeal.response_time.value]}> (<t:{appeal_message[Appeal.response_time.value]}:R>)"
                elif appeal_message[Appeal.response.value] == -1:
                    logs = f"{deny} **ID: {appeal_message[Appeal.id.value]}** at <t:{appeal_message[Appeal.response_time.value]}> (<t:{appeal_message[Appeal.response_time.value]}:R>)"
                else:
                    logs = f"{warn} **ID: {appeal_message[Appeal.id.value]}** at <t:{appeal_message[Appeal.response_time.value]}> (<t:{appeal_message[Appeal.response_time.value]}:R>)"



            if logs != "":
                embed.add_field(
                    name = _name,
                    value = logs,
                    inline = False
                )


            embed.add_field(
                name = "Sent at",
                value = f"<t:{sent_at}> (<t:{sent_at}:R>)",
                inline = False
            )

            embed.set_footer(
                text = f"Appeal ID: {appeal_id}"
            )
        except:
            raise ValueError()
        
        return embed


    def get_appeal_cooldown(self, guild, discord_id, cooldown):
        
        for appeal in reversed(appeals[guild]['handled_appeals']):
            if appeal[Appeal.discord_id.value] == discord_id:
                _time = round(time.time()) - appeal[Appeal.response_time.value]
                
                if appeal[Appeal.response.value] == -100:
                    cooldown *= 2
                
                if _time < cooldown:
                    return appeal[Appeal.response_time.value] + cooldown

        return 0
    

    def has_active_appeal(self, guild, discord_id):
        
        for appeal in appeals[guild]['sent_appeals']:
            if appeal[Appeal.discord_id.value] == discord_id:
                return True

        return False
    

    def get_appeal_id(self, string_id):
        id = re.search("\d+", string_id)

        return int(id.group(0))


    def get_appeal_sent_by_id(self, guild, appeal_id):
        
        for appeal in appeals[guild]['sent_appeals']:
            if appeal[Appeal.id.value] == appeal_id:
                return appeal

        return None


    def generate_new_appeal(self, guild, id):
        return [
            appeals[guild]['next_id'], # id

            round(time.time()), # created_at
            id, # discord_id
            0, # last_step

            "", # roblox_link
            0, # roblox_id
            "", # ban_reason
            "", # unban_reason

            0, # response_times
            0 # response
        ]


    def generate_log_embed(self, appeal_message, admin):

        appeal_id = appeal_message[Appeal.id.value]

        handled_at = round(time.time())

        user_id = appeal_message[Appeal.discord_id.value]
        user = self.bot.get_user(user_id)

        roblox_link = appeal_message[Appeal.roblox_link.value]
        roblox_id = appeal_message[Appeal.roblox_id.value]

        response = "Accepted"
        _color = 0x0ee320
        emoji = "<:greenTick:901197496276111451>"

        if appeal_message[Appeal.response.value] == -1:
            response = "Denied"
            _color = 0xe30e27
            emoji = "<:redTick:901197559912099841>"
        elif appeal_message[Appeal.response.value] == -100:
            response = "Warn"   
            _color = 0xd6c315
            emoji = "⚠️"

        embed = discord.Embed(
            color = _color
        )

        if user is not None:
            embed.set_author(
                name = f"{user}",
                icon_url = user.avatar_url
            )
        else:
            embed.set_author(
                name = "User left the server"
            )

        embed.add_field(
            name = "Discord Profile",
            value = f"{user.mention}  -  {user_id}",
            inline = False
        )    

        embed.add_field(
            name = "Roblox Profile",
            value = f"{roblox_link}  -  {roblox_id}",
            inline = False
        )                   
                   
        embed.add_field(
            name = "Handled at",
            value = f"<t:{handled_at}>",
            inline = False
        )

        embed.add_field(
            name = "Response",
            value = f"{emoji} {response}",
            inline = False
        )

        embed.add_field(
            name = "Admin",
            value = f"<@{admin}>",
            inline = False
        )

        embed.set_footer(
            text = f"Appeal ID: {appeal_id}"
        )

        return embed


    def cancel_appeal(self, guild, appeal_message):

        if appeal_message is not None:
            appeals[guild]['appeals'].remove(appeal_message)

            self.save_json()
            return True
        
        return False


    def get_discord_id_for_old_logs(self, message):

        reg = re.search("<@.*>", message)

        id = re.search("\d+", reg.group(0))

        return id.group(0)


    def get_roblox_id_for_old_logs(self, message):
        
        reg = re.search(":\*\*.*/", message)
        
        id = re.search("\d+", reg.group(0))

        return id.group(0)


    async def answer_appeal(self, guild, id, answer, admin):
        

        appeal_message = self.get_appeal_sent_by_id(guild, id)

        if appeal_message is None:
            return

        user_id = appeal_message[Appeal.discord_id.value]
        user = self.bot.get_user(user_id)

        appeal_message[Appeal.response.value] = answer
        appeal_message[Appeal.response_time.value] = round(time.time())


        appeals[guild]['sent_appeals'].remove(appeal_message)
        appeals[guild]['handled_appeals'].append(appeal_message)

        self.save_json()

        logs_channel_id = appeals[guild]['appeal_logs']
        logs_channel = self.bot.get_channel(logs_channel_id)

        await logs_channel.send(embed = self.generate_log_embed(appeal_message, admin))

        message_for_user = ""

        if answer == 1:
            message_for_user = f"Hello <@{user_id}>\n\nYou are unbanned from the game and have recieved a second chance\nIf you use Exploits / Hacks again your next ban will be permanent.\n\n"
        elif answer == -1:
            message_for_user = f"Hello <@{user_id}>\n\nYour ban appeal was reviewed by a administrator\nIt was denied and you can re-appeal your ban <t:{round(time.time() + appeals[guild]['cooldown'])}:R>\nYou are not able to appeal your ban anymore if you have been unbanned before\n\n"
        else:
            message_for_user = f"Hello <@{user_id}>\n\nYou have recentlly misused our ban appeal system.\nIf you continue to do so you will be punished."


        await user.send(message_for_user)


    async def create_appeal(self, interaction):
        
        interactionChannel = interaction.message.channel
        guild = self.bot.get_guild(interactionChannel.guild.id)

        if appeals[str(guild.id)]["accepting_appeals"] is True:

            member = guild.get_member(interaction.user.id)

            try:
                await member.send(f"Hello <@{member.id}>.\nType `Appeal` in order to continue!")

                await interaction.respond(
                    content = "You've got a message!"
                )
                
            except:
                await interaction.respond(
                    content = "Make sure your direct messages are **ON**! (Right click the server, press Privacy Settings and enable 'Allow direct messages from server members)"
                )
        else:
            await interaction.respond(
                content = "⛔ Appeals are closed at this time. Try again later."
            )


    async def delete_appeal(self, guild, id):

        appeal_message = self.get_appeal_sent_by_id(guild, id)

        if appeal_message is None:
            return

        appeals[guild]['sent_appeals'].remove(appeal_message)
        self.save_json()


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
    

    @commands.Cog.listener("on_ready")
    async def appeal_button_listener(self):
        
        while True:
            

            interaction = await self.bot.wait_for(
                'button_click'
            )

            id = interaction.custom_id
            guild = str(interaction.guild.id)


            #try:

            if id == "appeal_button":
                await self.create_appeal(interaction)
            elif id.startswith("accept_appeal_btn-"):
                await self.answer_appeal(guild, self.get_appeal_id(id), 1, interaction.author.id)
                await interaction.message.delete()
            elif id.startswith("deny_appeal_btn-"):
                await self.answer_appeal(guild, self.get_appeal_id(id), -1, interaction.author.id)
                await interaction.message.delete()
            elif id.startswith("delete_appeal_btn-"):
                await self.delete_appeal(guild, self.get_appeal_id(id))
                await interaction.message.delete()
            elif id.startswith("warn_appeal_btn-"):
                await self.answer_appeal(guild, self.get_appeal_id(id), -100, interaction.author.id)
                await interaction.message.delete()
            #except:
            #    print ("Unexpected error - Appeal Button Listener")
                

    @commands.Cog.listener("on_ready")
    async def dm_listener(self):
        
        guilds = {
            875089864998133780: "894160228239679490", # MAIN
            900101389416546314: "876988765955039273", # BURA
            867480262777765918: "852143372353142785" # AF
        }

        while True:

            message = await self.bot.wait_for(
                'message',
                check = lambda message: isinstance(message.channel, discord.DMChannel)
            )

            author =  message.author
            guild = guilds[self.bot.user.id]

            if appeals[guild]["accepting_appeals"] is True:

                try:

                    if not author.bot:
                        
                        id = author.id

                        steps = [
                            "You can cancel your appeal at any time by typing `Cancel`\n*Note: You have about 1 hour to submit the request before it auto cancels!*\n\n**First Question**\n> What is your roblox username?",
                            "**Second Question**\n> Why were you banned?",
                            "**Third Question**\n> Why do you think you should be unbanned?",
                            "**Your appeal has been sent!**\n"
                        ]

                        message_lower = message.content.lower().strip()

                        appeal_message = self.get_appeal_for_user(guild, id)

                        if message_lower == "appeal":
                            # create appeal message

                            if appeal_message is None:
                                
                                if self.has_active_appeal(guild, id) :
                                    await author.send(f"Hello <@{id}>\nYou are not able to appeal because your last appeal was not reviewed by the administration team.\nWe will message you soon about your appeal status.\n")
                                else:
                                    
                                    cooldown = self.get_appeal_cooldown(guild, id,  int(appeals[guild]['cooldown']))

                                    if cooldown != 0 and id != 225629057172111362:
                                        await author.send(f"Hello <@{id}>\nYou will be able to apply again <t:{cooldown}:R>, at <t:{cooldown}>")
                                    else:

                                        appeal_message = self.generate_new_appeal(guild, id)
                                        
                                        appeals[guild]['appeals'].append(appeal_message)

                                        await author.send(steps[0])

                                        appeals[guild]['next_id'] += 1
                                        
                                        self.save_json()
                            else:
                                await author.send("Please answer the question above or type `Cancel` in order to cancel your current request!")
                            
                        elif message_lower == "cancel":
                            
                            if self.cancel_appeal(guild, appeal_message) == True:
                                await author.send("Your appeal has been canceled!")

                        elif appeal_message is not None:
                            
                            last_step = appeal_message[Appeal.last_step.value]
                            

                            if last_step == 0: # roblox profile
                                
                                res = await author.send("<a:loading:901197462935580692> Searching profile...\n> Please wait")

                                profile = self.get_profile(message.content)
                                
                                if profile is None:
                                    await res.edit("Player not found. Please try again")
                                else:

                                    appeal_message[Appeal.roblox_link.value] = profile
                                    appeal_message[Appeal.roblox_id.value] = int(self.get_roblox_id(profile))
                                    appeal_message[Appeal.last_step.value] = 1

                                    await res.edit(steps[1])

                                    self.save_json()

                            elif last_step == 1: # ban_reason
                                
                                if len(message.content) == 0:
                                    await author.send("**The message can not be empty!**")
                                elif len(message.content) > 800:
                                    await author.send("**The message is too long.\nThe maximum amount of characters is** `800`**!**")
                                else:
                                    appeal_message[Appeal.ban_reason.value] = message.content
                                    appeal_message[Appeal.last_step.value] = 2

                                    await author.send(steps[2])

                                    self.save_json()
                            elif last_step == 2: # unban_reason

                                if len(message.content) == 0:
                                    await author.send("**The message can not be empty!**")
                                elif len(message.content) > 800:
                                    await author.send("**The message is too long.\nThe maximum amount of characters is** `800`**!**")
                                else:
                                    appeal_message[Appeal.unban_reason.value] = message.content
                                    appeal_message[Appeal.last_step.value] = 3

                                    # send appeal 

                                    appeal_channel_id = appeals[guild]['appeal_channel']
                                    appeal_channel = self.bot.get_channel(appeal_channel_id)

                                    self.save_json()

                                    comps = [
                                        [
                                            Button (
                                                style = ButtonStyle.green,
                                                label = "Accept",
                                                custom_id = f"accept_appeal_btn-{appeal_message[Appeal.id.value]}"
                                            ),
                                            Button (
                                                style = ButtonStyle.red,
                                                label = "Deny",
                                                custom_id = f"deny_appeal_btn-{appeal_message[Appeal.id.value]}"
                                            ),
                                            Button (
                                                style = ButtonStyle.blue,
                                                label = "Warn",
                                                custom_id = f"warn_appeal_btn-{appeal_message[Appeal.id.value]}"
                                            ),
                                            Button (
                                                style = ButtonStyle.gray,
                                                label = "Delete",
                                                custom_id = f"delete_appeal_btn-{appeal_message[Appeal.id.value]}"
                                            ),
                                        ]
                                    ]



                                    # try:


                                    await appeal_channel.send(
                                        embed = self.generate_appeal(guild, appeal_message),
                                        components = comps
                                    )

                                    appeals[guild]['sent_appeals'].append(appeal_message)


                                    await author.send(steps[3])

                                    # except:
                                    #     self.cancel_appeal(guild, appeal_message)
                                    #     await author.send("There was an error while sending the appeal.\nIf you see this message contact <@225629057172111362> (greater#2407).")
            

                                    appeals[guild]['appeals'].remove(appeal_message)
                                    self.save_json()
                        else:
                            await author.send("⛔ Appeals are closed at this time. Please try again later!")
                            
                except error:
                    print (error)
            

                
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_cooldown(self, ctx, time):

        time_in_seconds = self.convert_time(time)
        guild = str(ctx.channel.guild.id)

        if time_in_seconds in [-1, -2]:
            await ctx.channel.send("Unable to change the cooldown")
        else:
            appeals[guild]['cooldown'] = time_in_seconds
            self.save_json()

            await ctx.channel.send(f"Cooldown set to {time}")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_channel(self, ctx, channel : typing.Optional[discord.TextChannel]):

        if channel is None:
            channel = ctx.channelf

        appeals[str(ctx.channel.guild.id)]['appeal_channel'] = channel.id
        await ctx.send(f"<#{channel.id}> set as the main appeal channel.")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_log_channel(self, ctx, channel : typing.Optional[discord.TextChannel]):

        if channel is None:
            channel = ctx.channel

        appeals[str(ctx.channel.guild.id)]['appeal_logs'] = channel.id
        await ctx.send(f"<#{channel.id}> set as the main appeals log channel.")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def get_appeal(self, ctx, id):

        try:
            id = int(id)
        except ValueError as ve:
            await ctx.channel.send("Unable to find appeal with specified id")

        if type(id) == int:
            
            apps = appeals[str(ctx.channel.guild.id)]['handled_appeals']
            warns = appeals[str(ctx.channel.guild.id)]['warns']
            found = False

            for appeal in apps:
                if appeal[Appeal.id.value] == id:
                    await ctx.channel.send(embed = self.generate_appeal(appeal, False))
                    found = True

            for appeal in warns:
                if appeal[Appeal.id.value] == id:
                    await ctx.channel.send(embed = self.generate_appeal(appeal, False))
                    found = True

            if not found:
                await ctx.channel.send("Unable to find appeal with specified id")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def appeal_status(self, ctx, status):
        
        status = status.lower().strip()
        guild = ctx.guild

        if status in ["closed", "false", "0"]:
            appeals[str(guild.id)]["accepting_appeals"] = False
            await ctx.send("Appeals are now clsoed")
        elif status in ["open", "true", "1"]:
            appeals[str(guild.id)]["accepting_appeals"] = False
            await ctx.send("Appeal are now open")
        else:
            await ctx.send("Error")

        self.save_json()
       

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def logs(self, ctx, id):
        
        search_logs = True

        try:
            id = int(id.strip())
        except:
            await ctx.send("Invalid ID!\nMake sure you specify a **discord ID** or a **roblox ID**!")
            search_logs = False

        if search_logs:
            message = await ctx.send("Checking for logs...\nPlease wait!\n*I don't know how to make this faster, sorry*")

            logs = self.get_logs(ctx.channel.guild, id)

            if logs:
                await message.edit(logs)
            else:
                await message.edit("No logs found for this user!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def appeal(self, ctx, *, message = None):

        if message is not None:

            args = message.split(";")

            if len(args) != 4:
                return
            
            status = args[0].lower().strip()

            userID = int (args[1].strip())

            if userID == 0:
                return

            user = self.bot.get_user(userID)

            type = args[3].lower().strip()

            if (status != "accepted" and status != "denied") or (type != "game" and type != "discord"):
                return

            response = ""

            if type == "discord":
                response = "If you have a severe rule violation again your next ban will be permanent."
            elif type == "game":
                response = "If you use Exploits / Hacks again your next ban will be permanent."

            message_for_user = ""

            if status == "accepted":
                message_for_user = "Hello {}\n\nYou are unbanned from the {} and have recieved a second chance\n{}\n\n-Anime Fighters Administration Team".format(user.mention, type, response)
            elif status == "denied":
                message_for_user = "Hello {}\n\nYour ban appeal was reviewed by a administrator\nIt was denied and you can re-appeal your ban in 7 days\nYou are not able to appeal your ban anymore if you have been unbanned before\n\n-Anime Fighters Administration Team".format(user.mention)
            
            await user.send(message_for_user)
            await ctx.send("User DMed!\nMessage Context:\n{}".format(message_for_user))


    @tasks.loop(seconds = 2700.0)
    async def delete_appeals(self):
        
        for guild_id in appeals:
            guild_data = appeals[guild_id]
            for appeal in guild_data['appeals']:

                if appeal[Appeal.created_at.value] + guild_data['delete_time'] < round(time.time()):
                    
                    user = self.bot.get_user(appeal[Appeal.discord_id.value])
                    self.cancel_appeal(guild_id, appeal)
                    if user is not None:
                        await user.send("\nYour appeal has been canceled because it took you to long to respond.\nYou can create a new appeal request by typing `Appeal`")
        
        

with open('data/appeals.json') as appealsFile:
    appeals = json.load(appealsFile)
    appealsFile.close()


def setup(bot):
    bot.add_cog(Appeal_Module(bot))